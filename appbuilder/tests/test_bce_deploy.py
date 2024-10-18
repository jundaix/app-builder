import unittest
from unittest.mock import patch, MagicMock
import os
from appbuilder.utils.bce_deploy import AppbuilderSDKInstance

class TestAppbuilderSDKInstance(unittest.TestCase):

    @patch("appbuilder.utils.bce_deploy.BceCredentials")
    @patch("appbuilder.utils.bce_deploy.BosClient")
    @patch("appbuilder.utils.bce_deploy.InnerBccClient")
    @patch("appbuilder.utils.bce_deploy.logger")
    def setUp(self, MockLogger, MockInnerBccClient, MockBosClient, MockBceCredentials):
        self.config_path = "test_config.yaml"

        # 模拟配置文件读取
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

    @patch("appbuilder.utils.bce_deploy.BosClient.generate_pre_signed_url", return_value=b"http://test-url.com")
    @patch("appbuilder.utils.bce_deploy.BosClient.put_object_from_file")
    @patch("appbuilder.utils.bce_deploy.BosClient.does_bucket_exist", return_value=True)  # 确保存储桶已存在
    @patch("appbuilder.utils.bce_deploy.BosClient.create_bucket")  # 如果 bucket 不存在，模拟 bucket 创建
    @patch("appbuilder.utils.bce_deploy.logger")
    def test_bos_upload(self, mock_logger, mock_create_bucket, mock_does_bucket_exist, mock_put_object, mock_generate_url):
        self.instance.tar_file_name = "test_pkg.tar"
        
        # 调用 bos_upload 方法
        self.instance.bos_upload()


    @patch("appbuilder.utils.bce_deploy.InnerBccClient.create_instance_by_spec")
    def test_create_instance(self, mock_create_instance):
        # 创建模拟实例
        mock_instance = MagicMock()
        mock_instance.instance_ids = ["i-test-id"]
        mock_create_instance.return_value = mock_instance

        self.instance.tar_file_name = "test_pkg.tar"
        self.instance.tar_bos_url = "http://test-url.com"
        self.instance.run_script_name = "start_test.sh"
        
        self.instance.create_instance()
        
        # 验证 instance_id 是否正确
        

    @patch("appbuilder.utils.bce_deploy.InnerBccClient.get_instance")
    @patch("appbuilder.utils.bce_deploy.logger")
    def test_get_public_ip(self, mock_logger, mock_get_instance):
        # 模拟返回 public_ip 的响应
        mock_instance = MagicMock()
        mock_instance.public_ip = "127.0.0.1"
        mock_get_instance.return_value = MagicMock(instance=mock_instance)

        self.instance.instance_id = "i-test-id"
        self.instance.get_public_ip()

        # 验证 public_ip 是否正确
       

    @patch("builtins.open", new_callable=unittest.mock.mock_open)
    @patch("appbuilder.utils.bce_deploy.os.path.join", return_value="/tmp/start_test.sh")
    @patch("appbuilder.utils.bce_deploy.time.time", return_value=1234567890)  # 固定时间戳
    def test_build_run_script(self, mock_time, mock_path_join, mock_open):
        # 调用 build_run_script 方法
        self.instance.build_run_script()

        # 验证生成的脚本名称
        self.assertEqual(self.instance.run_script_name, "start_1234567890.sh")
        self.assertEqual(self.instance.run_script, "/tmp/start_test.sh")

        # 验证写入的脚本内容
        mock_open.assert_called_once_with("/tmp/start_test.sh", "w")
        mock_open().write.assert_any_call("#!/bin/sh\n")
        mock_open().write.assert_any_call("cd /workspace\n")
        mock_open().write.assert_any_call('export TEST_ENV="test_value" && echo test')

    @patch("appbuilder.utils.bce_deploy.AppbuilderSDKInstance.clear_local")
    @patch("appbuilder.utils.bce_deploy.AppbuilderSDKInstance.bos_upload")
    @patch("appbuilder.utils.bce_deploy.AppbuilderSDKInstance.create_tar")
    @patch("appbuilder.utils.bce_deploy.AppbuilderSDKInstance.build_run_script")
    @patch("appbuilder.utils.bce_deploy.logger")
    def test_pre_deploy(self, mock_logger, mock_build_run_script, mock_create_tar, mock_bos_upload, mock_clear_local):
        # 调用 _pre_deploy
        self.instance._pre_deploy()

        # 验证各个步骤是否被调用
        mock_build_run_script.assert_called_once()
        mock_create_tar.assert_called_once()
        mock_bos_upload.assert_called_once()
        mock_clear_local.assert_called_once()

    @patch("appbuilder.utils.bce_deploy.AppbuilderSDKInstance.create_instance")
    def test_deploy(self, mock_create_instance):
        # 调用 _deploy
        self.instance._deploy()

        # 验证 create_instance 是否被调用
        mock_create_instance.assert_called_once()

    @patch("appbuilder.utils.bce_deploy.AppbuilderSDKInstance.get_public_ip")
    @patch("appbuilder.utils.bce_deploy.AppbuilderSDKInstance.bind_security_group")
    @patch("appbuilder.utils.bce_deploy.logger")
    def test_after_deploy(self, mock_logger, mock_bind_security_group, mock_get_public_ip):
        self.instance.public_ip = "127.0.0.1"

        # 调用 _after_deploy
        self.instance._after_deploy()

    @patch("appbuilder.utils.bce_deploy.InnerBccClient.bind_instance_to_security_group")
    @patch("appbuilder.utils.bce_deploy.logger")
    def test_bind_security_group(self, mock_logger, mock_bind_instance_to_security_group):
        self.instance.instance_id = "i-mocked-instance"
        self.instance.security_group_id = "sg-mocked-id"

        # 调用 bind_security_group
        self.instance.bind_security_group()

    @patch("appbuilder.utils.bce_deploy.os.remove")
    def test_clear_local(self, mock_remove):
        # 模拟生成的文件名
        self.instance.run_script = "test_run_script.sh"
        self.instance.tar_file_name = "test_tar_file.tar"
        
        # 调用 clear_local
        self.instance.clear_local()

        # 验证 os.remove 是否被正确调用
        mock_remove.assert_any_call("test_run_script.sh")
        mock_remove.assert_any_call("test_tar_file.tar")

    def test_build_user_data(self):
        # 设置 tar 文件名和相关配置
        self.instance.tar_file_name = "test_tar_file.tar"
        self.instance.tar_bos_url = "http://test-url.com"
        self.instance.run_script_name = "start_script.sh"
        self.instance.appbuilder_config["workspace"] = "/workspace"

        # 调用 build_user_data
        user_data = self.instance.build_user_data()

        # 期望的 user_data 字符串
        expected_user_data = (
            "#!/bin/bash\\n"
            "mkdir /root/test\\n"
            "chmod 777 /root/test\\n"
            "cd /root/test\\n"
            "wget -O test_tar_file.tar http://test-url.com\\n"
            "tar -xvf test_tar_file.tar\\n"
            "rm test_tar_file.tar\\n"
            "chmod a+x start_script.sh\\n"
            "yum install -y docker\\n"
            "docker pull registry.baidubce.com/appbuilder/appbuilder-sdk-cloud:0.9.4\\n"
            "docker run -itd --net=host -v /root/test:/workspace --name appbuilder-sdk registry.baidubce.com/appbuilder/appbuilder-sdk-cloud:0.9.4/workspace/start_script.sh"
        )


if __name__ == "__main__":
    unittest.main()