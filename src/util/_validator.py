import logging

import jsonschema


def update_default_param(param, default_param):
    for key, item in default_param.items():
        param[key] = param.get(key, item)


REPORT_SCHEMA = {
    "title": "Report",
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "description": "어떤 시나리오의 레포트인지 식별하기 위한 이름"
        },
        "description": {
            "type": "string",
            "description": "해당 레포트가 정확히 어떤 시나리오를 다루는지 설명"
        },
        "report": {
            "type": "string",
            "description": "레포트 분석 결과"
        },
        "tags": {
            "type": "array",
            "items": {
                "type": "string",
                "enum": ["permission_denied",
                         "performance_degradation",
                         "pagecache"]
            },
            "description": "레포트에 대한 태그"
        },
        "metrics": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "time": {"type": "number"},
                    "value": {"type": "number"}
                }
            }
        },
        "affected": {
            "type": "array",
            "description": "해당 이슈로 영향을 받은것들",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string"},
                    "link": {"type": "string"},
                    "tag": {"type": "string",
                            "enum": ["resource", "host", "metric"]},
                }
            }
        }
    },
    "required": ["name", "description", "report"]
}

_report_validator = jsonschema.Draft7Validator(REPORT_SCHEMA)


def validate_report(report):
    for e in _report_validator.iter_errors(report, REPORT_SCHEMA):
        logging.error(e)
    else:
        return
    raise jsonschema.ValidationError
