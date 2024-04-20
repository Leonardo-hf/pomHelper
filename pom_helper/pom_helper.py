import logging
import os.path
import re
import time
from typing import List, Union, Optional, Callable, Final, Dict

import requests
from attr import dataclass
from lxml import etree

# A function which should accept 'group', 'artifact' & 'version' and return the content of the pom
Handler = Callable[[str, str, str], str]


# Default implement of the hanlder
# which use 'group', 'artifact' & 'version' to search the pom in maven central repository
def central_handler(group: str, artifact: str, version: str):
    return 'https://repo1.maven.org/maven2/{}/{}/{}/{}-{}.pom'.format(
        group.replace('.', '/'), artifact, version,
        artifact, version)


DEFAULT_HANDLERS: List[Handler] = [
    central_handler
]

TAG_GROUP = "groupId"
TAG_ARTIFACT = "artifactId"
TAG_VERSION = "version"
TAG_PARENT = "parent"
TAG_DEPENDENCIES_MANAGE = "dependencyManagement"
TAG_DEPENDENCIES = "dependencies"
TAG_DEPENDENCY = "dependency"
TAG_OPTIONAL = "optional"
TAG_SCOPE = "scope"
TAG_PROPERTIES = "properties"
TAG_PROFILES = "profiles"
TAG_PROFILE = "profile"
TAG_PROFILE_ID = "id"

UNDEFINED = "$undefined"


class POMError(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return '[POM] {}'.format(self.message)


# Fail to find the content of the pom in a right formal by the given coordinate
ERR_INVALID = POMError('invalid constructor parameter')


# Fail to indentify the key attribute in the pom
def fail_to_identity(e):
    raise POMError('cannot identify {}'.format(e))


def is_undefined(v: Optional[str]):
    return v == UNDEFINED


def is_none(v):
    return v is None


def is_valid(v):
    return not is_undefined(v) and not is_none(v)


@dataclass(hash=True, eq=True)
class Package:
    artifact: str
    group: str
    version: str


@dataclass(hash=True, eq=True)
class Dependency(Package):
    scope: str
    optional: bool


class POM:

    def __init__(self):
        self._root = UNDEFINED
        self._namespace: Union[str, None] = UNDEFINED
        self._artifact: Union[str, None] = UNDEFINED
        self._group: Union[str, None] = UNDEFINED
        self._version: Union[str, None] = UNDEFINED
        self._dependencies: Union[List[Dependency], str, None] = UNDEFINED
        self._dependencies_management: Union[List[Dependency], str, None] = UNDEFINED
        self._properties: Union[Dict[str, str], str, None] = UNDEFINED
        self._profiles: Union[Dict[str, POM], str, None] = UNDEFINED
        self._parent: Union[POM, str, None] = UNDEFINED
        self._plain: Union[str, None] = UNDEFINED
        self._urls: Union[List[str], str, None] = UNDEFINED
        self._url_handlers: Union[Handler, str, None] = UNDEFINED
        self._re_namespace: Final[re.Pattern] = re.compile('({.*?})')
        self._re_ref: Final[re.Pattern] = re.compile('(\\${.*?})')

    def iter(self, node, tag):
        return node.iter(self._namespace + tag)

    def search(self, node, tag):
        v = node.find(self._namespace + tag)
        if is_none(v):
            return None
        return v

    def value(self, node, tag):
        v = node.find(self._namespace + tag)
        if is_none(v):
            return None
        return v.text

    def value_or_default(self, node, tag, default):
        v = self.value(node, tag)
        if is_none(v):
            return default
        return v

    def get_root(self):
        if not is_undefined(self._root):
            return self._root
        # build root from plain text
        if not is_undefined(self._plain):
            if is_none(self._plain):
                raise ERR_INVALID
            # TODO: delete invalid prefix
            self._plain = self._plain[self._plain.find('<'):]
            self._root = etree.fromstring(self._plain.encode('UTF-8'),
                                          parser=etree.XMLParser(remove_comments=True, remove_pis=True, recover=True))
            try:
                self._namespace = self._re_namespace.search(self._root.tag).group(1)
            except AttributeError:
                self._namespace = ''
            return self._root
        # build plain from urls, and do again
        if is_valid(self._urls):
            self._plain = fetch(self._urls)
            return self.get_root()
        # build url from coordinate, and do again
        if is_valid(self._group) and is_valid(self._artifact) and is_valid(self._version):
            self._urls = list(map(lambda h: h(self._group, self._artifact, self._version), self._url_handlers))
            return self.get_root()
        raise ERR_INVALID

    def get_group_id(self):
        if not is_undefined(self._group):
            return self._group
        root = self.get_root()
        # search <groupId>
        v = self.value(root, TAG_GROUP)
        if is_none(v):
            parent = self.get_parent()
            if is_none(parent):
                fail_to_identity(TAG_PARENT)
            v = parent.get_group_id()
        self._group = v
        return v

    def get_artifact(self):
        if not is_undefined(self._artifact):
            return self._artifact
        root = self.get_root()
        # search <artifact>
        v = self.value(root, TAG_ARTIFACT)
        if is_none(v):
            fail_to_identity(TAG_ARTIFACT)
        self._artifact = v
        return v

    def get_version(self):
        if not is_undefined(self._version):
            return self._version
        root = self.get_root()
        # search <version>
        v = self.value(root, TAG_VERSION)
        # if version is none, use parent's version
        if is_none(v):
            parent = self.get_parent()
            if is_none(parent):
                fail_to_identity(TAG_PARENT)
            v = parent.get_version()
        # check if version has ${XXX}
        v = self._check_ref(v)
        self._version = v
        return v

    def get_dependencies(self):
        if not is_undefined(self._dependencies):
            return self._dependencies
        dependencies = {}
        root = self.get_root()
        # search <dependencies>
        deps = self.search(root, TAG_DEPENDENCIES)
        if not is_none(deps):
            for d in self._extract_dependencies(deps):
                dependencies.setdefault((d.group, d.artifact), d)
        # add parent's dependencies, ignore redundant
        if not is_none(self.get_parent()):
            for d in self.get_parent().get_dependencies():
                dependencies.setdefault((d.group, d.artifact), d)
        self._dependencies = list(dependencies.values())
        return self._dependencies

    def get_dependencies_management(self):
        if not is_undefined(self._dependencies_management):
            return self._dependencies_management
        dependencies_management = {}
        root = self.get_root()
        # search <dependencyManagement>
        deps_manage = self.search(root, TAG_DEPENDENCIES_MANAGE)
        if not is_none(deps_manage):
            # search <dependencyManagement.dependencies>
            deps = self.search(deps_manage, TAG_DEPENDENCIES)
            if not is_none(deps):
                for d in self._extract_dependencies(deps, is_manage=True):
                    dependencies_management.setdefault((d.group, d.artifact), d)
        # add parent's dependencies_management, ignore redundant
        if not is_none(self.get_parent()):
            for d in self.get_parent().get_dependencies_management():
                dependencies_management.setdefault((d.group, d.artifact), d)
        self._dependencies_management = list(dependencies_management.values())
        return self._dependencies_management

    def get_profiles(self):
        if not is_undefined(self._profiles):
            return self._profiles
        root = self.get_root()
        # search <profiles>
        profiles = self.search(root, TAG_PROFILES)
        if is_none(profiles):
            self._profiles = None
            return None
        # search <profiles.profile>
        self._profiles = {}
        for profile in self.iter(profiles, TAG_PROFILE):
            pid = self.value(profile, TAG_PROFILE_ID)
            pom = self.from_coordinate(group=self.get_group_id(), artifact=self.get_artifact(),
                                       version=self.get_version(), url_handlers=self._url_handlers)
            pom._plain = etree.tostring(profile).decode()
            pom._parent = pom.get_parent()
            if is_none(pom.get_properties()):
                pom._properties = self.get_properties()
            else:
                pom._properties = pom.get_properties().update(self.get_properties())
            self._profiles[pid] = pom
        return self._profiles

    def _check_ref(self, field: str) -> str:
        # TODO: if field is blank, it may be switched by profile
        if not field:
            return ''
        # may be ${xxx}-${yyy}
        refs = self._re_ref.findall(field)
        for r in refs:
            key = v = r[2:-1]
            s = self
            # if not found, search in parent's properties
            while not is_none(s):
                # if ${project.version}, use project's version
                if key == 'project.version':
                    v = s.get_version()
                    break
                # if ${project.parent.version}, use project's parent's version
                if key == 'project.parent.version':
                    # TODO: but if there is no parent,
                    if is_none(s.get_parent()):
                        v = 'None'
                        break
                    v = s.get_parent().get_version()
                    break
                properties = s.get_properties()
                # if <XXX> = ${XXX}, search its parent
                if not is_none(properties) and key in properties and properties[key] != r:
                    v = properties[key]
                    break
                s = s.get_parent()
            # not found, there must be an error
            if v == key:
                fail_to_identity('ref')
            # it should get, but may still be ${XXX} or ${project.version}, so check again
            v = self._check_ref(v)
            field = field.replace(r, v)
        return field

    def _extract_dependencies(self, deps, is_manage=False) -> List[Dependency]:
        dependencies = []
        for dep in self.iter(deps, TAG_DEPENDENCY):
            # get artifact
            artifact = self.value(dep, TAG_ARTIFACT)
            artifact = self._check_ref(artifact)
            # if artifact is `unspecified`, skip
            if artifact == 'unspecified':
                continue
            # get group
            group = self.value(dep, TAG_GROUP)
            if group == '${project.groupId}':
                group = self.get_group_id()
            group = self._check_ref(group)
            # get version
            version = self.value(dep, TAG_VERSION)
            # get scope & optional
            scope = self.value_or_default(dep, TAG_SCOPE, default='compile')
            optional = bool(self.value_or_default(dep, TAG_OPTIONAL, default=False))
            # version is ${XXX} search in properties
            if not is_none(version):
                version = self._check_ref(version)
            # version is none, search in self and parent's management
            if is_none(version) and not is_manage:
                s = self
                while not is_none(s) and is_none(version):
                    pdeps = s.get_dependencies_management()
                    s = s.get_parent()
                    if is_none(pdeps):
                        continue
                    try:
                        version = next(d for d in pdeps if group == d.group and artifact == d.artifact).version
                    except StopIteration:
                        continue
            # while parsing dependencyManagement,
            # scope `import` means importing extra dependencyManagement from target pom
            if is_manage and scope == 'import':
                target = self.from_coordinate(artifact=artifact, group=group, version=version,
                                              url_handlers=self._url_handlers)
                deps = target.get_dependencies_management()
                if not is_none(deps):
                    dependencies.extend(deps)
            dependencies.append(
                Dependency(group=group, artifact=artifact, version=version, scope=scope, optional=optional))
        return dependencies

    def get_properties(self):
        if not is_undefined(self._properties):
            return self._properties
        root = self.get_root()
        v = self.search(root, TAG_PROPERTIES)
        self._properties = v
        if not is_none(v):
            self._properties = {}
            for p in v:
                self._properties[p.tag[len(self._namespace):]] = p.text
        return self._properties

    def get_parent(self):
        if not is_undefined(self._parent):
            return self._parent
        root = self.get_root()
        parent = self.search(root, TAG_PARENT)
        if is_none(parent):
            self._parent = None
            return self._parent
        group = self.value(parent, TAG_GROUP)
        artifact = self.value(parent, TAG_ARTIFACT)
        version = self.value(parent, TAG_VERSION)
        version = self._check_ref(version)
        self._parent = self.from_coordinate(artifact=artifact, group=group, version=version,
                                            url_handlers=self._url_handlers)
        return self._parent

    @classmethod
    def from_coordinate(cls, group: str, artifact: str, version: str, url_handlers: List[Handler] = DEFAULT_HANDLERS):
        pom = cls()
        pom._artifact = artifact
        pom._group = group
        pom._version = version
        pom._url_handlers = url_handlers
        return pom

    @classmethod
    def from_string(cls, plain: str, url_handlers: List[Handler] = DEFAULT_HANDLERS):
        pom = cls()
        pom._plain = plain
        pom._url_handlers = url_handlers
        return pom

    @classmethod
    def from_url(cls, url: str, url_handlers: List[Handler] = DEFAULT_HANDLERS):
        return cls.from_urls([url], url_handlers=url_handlers)

    @classmethod
    def from_urls(cls, urls: List[str], url_handlers: List[Handler] = DEFAULT_HANDLERS):
        pom = cls()
        pom._urls = urls
        pom._url_handlers = url_handlers
        return pom


def fetch(urls: List[str]) -> Union[str, None]:
    for url in urls:
        if url.startswith('file://'):
            url = url[7:]
            if os.path.exists(url):
                with open(url, 'r') as f:
                    return f.read()
            continue
        logging.warning('[POM] downloading {}...'.format(url))
        while True:
            try:
                res = requests.get(url)
                if res.status_code == 404:
                    logging.warning('[POM] download {} fail, file has been deleted from repository.'.format(url))
                    break
                html = res.text
                return html
            except Exception as e:
                logging.error(e)
    return None
