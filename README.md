# pomHelper

A helper for parsing `.pom`

### Constructors:

* from_coordinate
* from_string
* from_url/from_urls

### Functions:

* get_group_id
* get_artifact
* get_version
* get_dependencies
* get_dependencies_management
* get_profiles
* get_properties
* get_parent

### Cases

More cases in `pom_helper/test`

```python
from pom_helper import POM, DEFAULT_HANDLERS

basedir = '/test'


def local_handler(group: str, artifact: str, version: str):
    return 'file://{}/{}.{}.{}.pom'.format(basedir, group, artifact, version)


URL_HANDLERS = [
    DEFAULT_HANDLERS,
    local_handler
]

pom = POM.from_coordinate('test-groupid', 'test-artifact', 'test-version', url_handlers=URL_HANDLERS)
g = pom.get_group_id()
a = pom.get_artifact()
v = pom.get_version()
deps = pom.get_dependencies()
if deps:
    for d in deps:
        tg = d.group
        ta = d.artifact
        tv = d.version
        print(g, a, v, tg, ta, tv)
```