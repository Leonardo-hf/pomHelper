from pom_helper import POM, Dependency


def test_with_properties():
    f = open('pom_helper/test/cases/au.csiro.aehrc.variant-spark.variant-spark_2.12.0.5.2.pom', 'r')
    p = POM.from_string(f.read())
    assert p.get_group_id() == 'au.csiro.aehrc.variant-spark' and p.get_artifact() == 'variant-spark_2.12' and p.get_version() == '0.5.2'
    assert set(p.get_dependencies()) == {
        Dependency(artifact='scala-library', group='org.scala-lang', version='2.12.14', scope='provided',
                   optional=False),
        Dependency(artifact='spark-core_2.12', group='org.apache.spark', version='3.1.2', scope='provided',
                   optional=False),
        Dependency(artifact='spark-mllib_2.12', group='org.apache.spark', version='3.1.2', scope='provided',
                   optional=False),
        Dependency(artifact='graph-core_2.12', group='org.scala-graph', version='1.12.3', scope='compile',
                   optional=False),
        Dependency(artifact='junit', group='junit', version='4.13.1', scope='test', optional=False),
        Dependency(artifact='fastutil', group='it.unimi.dsi', version='7.0.8', scope='compile', optional=False),
        Dependency(artifact='scala-csv_2.12', group='com.github.tototoshi', version='1.3.8', scope='compile',
                   optional=False),
        Dependency(artifact='htsjdk', group='com.github.samtools', version='2.21.0', scope='compile', optional=False),
        Dependency(artifact='joda-time', group='joda-time', version='2.7', scope='compile', optional=False),
        Dependency(artifact='args4j', group='args4j', version='2.0.29', scope='compile', optional=False),
        Dependency(artifact='json4s-ext_2.12', group='org.json4s', version='3.5.3', scope='compile', optional=False),
        Dependency(artifact='dsiutils', group='it.unimi.dsi', version='2.3.3', scope='compile', optional=False),
        Dependency(artifact='easymock', group='org.easymock', version='3.5.1', scope='test', optional=False),
        Dependency(artifact='asm', group='org.ow2.asm', version='5.1', scope='provided', optional=False),
        Dependency(artifact='asm-util', group='org.ow2.asm', version='5.1', scope='provided', optional=False),
        Dependency(artifact='asm-analysis', group='org.ow2.asm', version='5.1', scope='provided', optional=False),
        Dependency(artifact='hail_2.12_3.1', group='au.csiro.aehrc.third.hail-is', version='0.2.74-SNAPSHOT',
                   scope='provided', optional=False),
        Dependency(artifact='commons-csv', group='org.apache.commons', version='1.9.0', scope='test', optional=False)
    }


def test_with_management():
    p = POM.from_coordinate('au.csiro.pathling', 'library-api', '6.3.1')
    assert p.get_group_id() == 'au.csiro.pathling' and p.get_artifact() == 'library-api' and p.get_version() == '6.3.1'
    assert set(p.get_dependencies()) == {
        Dependency(artifact='jakarta.validation-api', group='jakarta.validation', version='2.0.2', scope='compile',
                   optional=False),
        Dependency(artifact='terminology', group='au.csiro.pathling', version='6.3.1', scope='compile', optional=False),
        Dependency(artifact='hapi-fhir-structures-r4', group='ca.uhn.hapi.fhir', version='6.6.1', scope='compile',
                   optional=False),
        Dependency(artifact='utilities', group='au.csiro.pathling', version='6.3.1', scope='compile', optional=False),
        Dependency(artifact='mockito-core', group='org.mockito', version='4.8.1', scope='test', optional=False),
        Dependency(artifact='junit-jupiter-params', group='org.junit.jupiter', version='5.9.1', scope='test',
                   optional=False),
        Dependency(artifact='commons-io', group='commons-io', version='2.11.0', scope='compile', optional=False),
        Dependency(artifact='logback-classic', group='ch.qos.logback', version='1.4.4', scope='test', optional=False),
        Dependency(artifact='delta-core_2.12', group='io.delta', version='2.3.0', scope='provided', optional=False),
        Dependency(artifact='fhirpath', group='au.csiro.pathling', version='6.3.1', scope='compile', optional=False),
        Dependency(artifact='commons-lang3', group='org.apache.commons', version='3.12.0', scope='compile',
                   optional=False),
        Dependency(artifact='junit-jupiter-engine', group='org.junit.jupiter', version='5.9.1', scope='test',
                   optional=False),
        Dependency(artifact='junit-jupiter-api', group='org.junit.jupiter', version='5.9.1', scope='test',
                   optional=False),
        Dependency(artifact='guava', group='com.google.guava', version='31.0.1-jre', scope='compile', optional=False),
        Dependency(artifact='spark-hive_2.12', group='org.apache.spark', version='3.3.2', scope='test', optional=False),
        Dependency(artifact='spark-core_2.12', group='org.apache.spark', version='3.3.2', scope='provided',
                   optional=False),
        Dependency(artifact='hadoop-client-api', group='org.apache.hadoop', version='3.3.4', scope='provided',
                   optional=False),
        Dependency(artifact='encoders', group='au.csiro.pathling', version='6.3.1', scope='compile', optional=False),
        Dependency(artifact='scala-library', group='org.scala-lang', version='2.12.17', scope='provided',
                   optional=False),
        Dependency(artifact='slf4j-api', group='org.slf4j', version='2.0.3', scope='provided', optional=False),
        Dependency(artifact='jsr305', group='com.google.code.findbugs', version='3.0.2', scope='provided',
                   optional=False),
        Dependency(artifact='spark-catalyst_2.12', group='org.apache.spark', version='3.3.2', scope='provided',
                   optional=False),
        Dependency(artifact='lombok', group='org.projectlombok', version='1.18.28', scope='provided', optional=False),
        Dependency(artifact='hapi-fhir-base', group='ca.uhn.hapi.fhir', version='6.6.1', scope='compile',
                   optional=False),
        Dependency(artifact='spark-sql_2.12', group='org.apache.spark', version='3.3.2', scope='provided',
                   optional=False)}
