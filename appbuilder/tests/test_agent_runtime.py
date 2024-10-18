import unittest
from unittest.mock import patch, MagicMock
import os
import sys

from appbuilder.core.agent import AgentRuntime
from appbuilder.core.component import Component
from appbuilder import AppBuilderClient

class TestAgentRuntimeChainlitAgent(unittest.TestCase):

    @patch('appbuilder.core.agent.AgentRuntime.prepare_chainlit_readme')
    @patch('appbuilder.core.agent.AgentRuntime.chainlit_agent')
    def test_chainlit_agent_with_valid_component(self, mock_prepare, mock_chainlit_agent):
        # 创建一个 AppBuilderClient 的 mock 实例
        mock_component = MagicMock(spec=AppBuilderClient)
        agent = AgentRuntime(component=mock_component)

        with patch.dict('sys.modules', {'chainlit': MagicMock(), 'chainlit.cli': MagicMock()}):
            with patch('click.testing.CliRunner.invoke') as mock_invoke:
                agent.chainlit_agent(host='127.0.0.1', port=8080)
                # 检查 prepare_chainlit_readme 是否被调用
                mock_prepare.assert_called_once()
                # 检查 chainlit_run 是否被调用
                mock_invoke.assert_called()
                # 检查环境变量是否被设置
                self.assertEqual(os.getenv('APPBUILDER_RUN_CHAINLIT'), '1')

    def test_chainlit_agent_with_invalid_component(self):
        # 创建一个非 AppBuilderClient 的组件
        mock_component = MagicMock(spec=Component)
        agent = AgentRuntime(component=mock_component)

        with self.assertRaises(ValueError) as context:
            agent.chainlit_agent()
        self.assertIn("chainlit_agent require component must be an instance of AppBuilderClient", str(context.exception))

    @patch.dict('sys.modules', {})
    def test_chainlit_agent_missing_chainlit(self):
        mock_component = MagicMock(spec=AppBuilderClient)
        agent = AgentRuntime(component=mock_component)

        with self.assertRaises(ImportError) as context:
            agent.chainlit_agent()
        self.assertIn("chainlit module is not installed. Please install it using 'pip install chainlit~=1.0.200'.", str(context.exception))

    @patch('appbuilder.core.agent.AgentRuntime.prepare_chainlit_readme')
    @patch('appbuilder.core.agent.AppBuilderClient.create_conversation')
    @patch('appbuilder.core.agent.CliRunner.invoke')
    def test_chainlit_agent_environment_already_set(self, mock_invoke, mock_create_conversation, mock_prepare):
        # 模拟环境变量已设置
        os.environ['APPBUILDER_RUN_CHAINLIT'] = '1'

        mock_component = MagicMock(spec=AppBuilderClient)
        agent = AgentRuntime(component=mock_component)

        with patch('sys.modules', {'chainlit': MagicMock(), 'chainlit.cli': MagicMock()}):
            agent.chainlit_agent(host='127.0.0.1', port=8080)
            # prepare_chainlit_readme 应被调用
            mock_prepare.assert_called_once()
            # 因为环境变量已设置，不应调用 chainlit_run
            mock_invoke.assert_not_called()

        # 清理环境变量
        del os.environ['APPBUILDER_RUN_CHAINLIT']

if __name__ == '__main__':
    unittest.main()