# Copyright (c) 2024 Baidu, Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import os
import unittest
from typing import Optional, Union
from inspect import Parameter,Signature,Annotated
from appbuilder.utils.tool_definition_signature import get_signature_view, _parse_annotation, _parse_internal_annotation, _parse_parameter

@unittest.skipUnless(os.getenv("TEST_CASE", "UNKNOWN") == "CPU_SERIAL", "")

class TestToolDefinitionSignature(unittest.TestCase):

    # 示例函数，包含多种类型的参数注解和返回类型
    def sample_func(a: int, b: Optional[str] = None) -> Union[int, None]:
        return a

    # 没有注解和默认值的函数
    def func_no_annotations(x):
        return x

    # 测试 get_signature_view 函数
    def test_get_signature_view(self):
        params, returns = get_signature_view(self.sample_func)
        assert params == [
            {'type_': 'int', 'required': True, 'name': 'a'},
            {'type_': 'str', 'required': False, 'name': 'b', 'default_value': None}
        ]
        assert returns == {'type_': 'Union[int, None]', 'required': False}

        # 测试没有注解的情况
        params, returns = get_signature_view(self.func_no_annotations)
        assert params == [{'type_': 'Any', 'required': True, 'name': 'x'}]
        assert returns == {}

    # 测试 _parse_parameter 函数
    def test_parse_parameter(self):
        param_no_default = Parameter("x", Parameter.POSITIONAL_OR_KEYWORD, annotation=int)
        param_with_default = Parameter("y", Parameter.POSITIONAL_OR_KEYWORD, annotation=str, default="test")

        result_no_default = _parse_parameter(param_no_default)
        assert result_no_default == {'type_': 'int', 'required': True, 'name': 'x'}

        result_with_default = _parse_parameter(param_with_default)
        assert result_with_default == {'type_': 'str', 'required': False, 'name': 'y', 'default_value': 'test'}

    # 测试 _parse_annotation 函数
    def test_parse_annotation(self):
        assert _parse_annotation(int) == {'type_': 'int', 'required': True}
        assert _parse_annotation(Optional[int]) == {'type_': 'Optional[int]', 'required': False}
        assert _parse_annotation(Union[int, None]) == {'type_': 'Union[int, None]', 'required': False}
        assert _parse_annotation("CustomType") == {'type_': 'CustomType', 'required': True}
        
        # 触发 annotation == Signature.empty
        assert _parse_annotation(Signature.empty) == {'type_': 'Any', 'required': True}

        # 触发带有 __metadata__ 的注解
        annotated_type = Annotated[int, "example metadata"]
        result = _parse_annotation(annotated_type)
        assert 'type_' in result
        assert 'required' in result
        assert 'description' in result

    # 测试 _parse_internal_annotation 函数
    def test_parse_internal_annotation(self):
        # 基本类型的测试
        assert _parse_internal_annotation(int, True) == {'type_': 'int', 'type_object': int, 'required': True}
        assert _parse_internal_annotation(Optional[int], True) == {'type_': 'Optional[int]', 'required': False}
        assert _parse_internal_annotation(Union[int, None], True) == {'type_': 'Union[int, None]', 'required': False}
        assert _parse_internal_annotation(Union[int, str], True) == {
            'type_': 'Union[int, str]', 'required': True
        }
        # 复合类型的测试
        complex_type = Union[Optional[int], str]
        result = _parse_internal_annotation(complex_type, True)
        assert result['type_'] == 'Union[Optional[int], str]'
        assert result['required'] == True

        # 触发 __forward_arg__ 的情况
        class ForwardReference:
            __forward_arg__ = "ForwardType"
        assert _parse_internal_annotation(ForwardReference, True) == {'type_': 'ForwardReference', 'required': True}
        
        # 触发 parent_type == "Union" 且 all optionals are optional 的情况
        mixed_union_type = Union[Optional[int], None]
        result = _parse_internal_annotation(mixed_union_type, True)
        assert result['required'] == False

if __name__ == '__main__':
    unittest.main()