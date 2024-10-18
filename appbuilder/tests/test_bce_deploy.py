import unittest
from unittest.mock import patch, MagicMock
from appbuilder.utils.bce_deploy import AppbuilderSDKInstance

class TestAppbuilderSDKInstance(unittest.TestCase):

    @patch("appbuilder.utils.bce_deploy.BceCredentials")
    @patch("appbuilder.utils.bce_deploy.BosClient")
    @patch("appbuilder.utils.bce_deploy.InnerBccClient")
    @patch("appbuilder.utils.bce_deploy.logger")
    def setUp(self, MockLogger, MockInnerBccClient, MockBosClient, MockBceCredentials):
        self.config_path = "test_config.yaml"

        with patch("builtins.open", unittest.mock.mock_open(read_data="""
        bce_config:
          ak: "test_ak"
          sk: "test_sk"
          host: "test_host"
          bos_host: "test_bos_host"
          security_group_id: "test_sg_id"
          admin_pass: "test_admin_pass"
          zone_name: "test_zone"
          root_disk_size_in_gb: 40
          spec: "test_spec"
        appbuilder_config:
          local_dir: "/tmp"
          workspace: "/workspace"
          run_cmd: "echo test"
        env:
          TEST_ENV: "test_value"
        """)):
            self.instance = AppbuilderSDKInstance(self.config_path)

        # 手动为 log 赋值
        self.instance.log = MockLogger

    def test_load_config(self):
        with patch("builtins.open", unittest.mock.mock_open(read_data="""
        bce_config:
          ak: "test_ak"
          sk: "test_sk"
          host: "test_host"
          bos_host: "test_bos_host"
          security_group_id: "test_sg_id"
          admin_pass: "test_admin_pass"
          zone_name: "test_zone"
          root_disk_size_in_gb: 40
          spec: "test_spec"
        appbuilder_config:
          local_dir: "/tmp"
          workspace: "/workspace"
          run_cmd: "echo test"
        env:
          TEST_ENV: "test_value"
        """)):
            self.instance.load_config()
        self.assertEqual(self.instance.bce_config["ak"], "test_ak")
        self.assertEqual(self.instance.appbuilder_config["workspace"], "/workspace")

    @patch("appbuilder.utils.bce_deploy.BosClient")
    def test_create_bos_client(self, MockBosClient):
        bos_client = self.instance.create_bos_client()
        self.assertIsNotNone(bos_client)

    @patch("appbuilder.utils.bce_deploy.InnerBccClient")
    def test_create_bce_client(self, MockInnerBccClient):
        bce_client = self.instance.create_bce_client()
        self.assertIsNotNone(bce_client)

if __name__ == "__main__":
    unittest.main()