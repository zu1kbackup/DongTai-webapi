######################################################################
# @author      : bidaya0 (bidaya0@$HOSTNAME)
# @file        : test_vul_details
# @created     : 星期四 12月 09, 2021 10:23:10 CST
#
# @description :
######################################################################



from django.test import TestCase
from django.urls import include, path, reverse
from dongtai.models.user import User
from dongtai.models.vulnerablity import IastVulnerabilityModel
from dongtai.models.hook_type import HookType
import time
from ddt import ddt, data, unpack
from iast.serializers.vul import VulSerializer

TEST_DATA = ('', None, 'Django', 'Apache Tomcat/9.0.37', 'Tomcat/8.x',
             'php-fpm', 'WebLogic')

@ddt
class VulTestCase(TestCase):
    def setUp(self):
        pass

    @data(*TEST_DATA)
    def test_vul(self, value):
        try:
            res = VulSerializer.split_container_name(value)
        except Exception as e:
            self.fail("raised Exception:{}".format(e))
        assert isinstance(res, str)

    def tearDown(self):
        pass
