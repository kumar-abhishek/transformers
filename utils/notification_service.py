# Copyright 2020 The HuggingFace Team. All rights reserved.
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

import json
import sys
import requests


def handle_test_results(test_results):
    expressions = test_results.split(" ")

    failed = 0
    success = 0
    time_spent = expressions[-2]

    for i, expression in enumerate(expressions):
        if "failed" in expression:
            failed += int(expressions[i - 1])
        if "passed" in expression:
            success += int(expressions[i - 1])

    return failed, success, time_spent


def format_for_slack_with_failures(total_results, results):
    print(results)
    header = {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "🤗 Results of the scheduled tests, March 11, 2021.",
            "emoji": True
        }
    }

    total = {
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*Failures:*\n❌ {total_results['failed']} failures."
            },
            {
                "type": "mrkdwn",
                "text": f"*Passed:*\n✅ {total_results['success']} tests passed."
            },
        ]
    } if total_results['failed'] > 0 else {
        "type": "section",
        "fields": [
            {
                "type": "mrkdwn",
                "text": f"*Congrats!*\nAll {total_results['success']} tests pass."
            }
        ]
    }

    blocks = [header, total]

    if total_results['failed'] > 0:
        for key, result in results.items():
            print(key, result)
            blocks.append(
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": key,
                        "emoji": True
                    }
                }
            )
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Results:*\n{result['failed']} failed, {result['success']} passed."
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Time spent:*\n{result['time_spent']}"
                    }
                ]
            })
    else:
        for key, result in results.items():
            blocks.append({
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*{key}*\n{result['time_spent']}."
                    }
                ]
            })

    footer = {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "<https://github.com/huggingface/transformers/actions/workflows/self-scheduled.yml|View on GitHub>"
        }
    }

    blocks.append(footer)

    blocks = {
        "blocks": blocks
    }

    return blocks


if __name__ == "__main__":
    scheduled = sys.argv[1] == "scheduled"

    if scheduled:
        file_paths = {
            "TF Single GPU": {
                "common": "run_all_tests_tf_gpu_test_reports/tests_tf_gpu_stats.txt",
                "pipeline": "run_all_tests_tf_gpu_test_reports/tests_tf_pipeline_gpu_stats.txt",
            },
            "Torch Single GPU": {
                "common": "run_all_tests_torch_gpu_test_reports/tests_torch_gpu_stats.txt",
                "pipeline": "run_all_tests_torch_gpu_test_reports/tests_torch_pipeline_gpu_stats.txt",
                "examples": "run_all_tests_torch_gpu_test_reports/examples_torch_gpu_stats.txt",
            },
            "TF Multi GPU": {
                "common": "run_all_tests_tf_multi_gpu_test_reports/tests_tf_multi_gpu_stats.txt",
                "pipeline": "run_all_tests_tf_multi_gpu_test_reports/tests_tf_pipeline_multi_gpu_stats.txt",
            },
            "Torch Multi GPU": {
                "common": "run_all_tests_torch_multi_gpu_test_reports/tests_torch_multi_gpu_stats.txt",
                "pipeline": "run_all_tests_torch_multi_gpu_test_reports/tests_torch_pipeline_multi_gpu_stats.txt",
            }
        }
    else:
        file_paths = {
            "TF Single GPU": {
                "common": "run_all_tests_tf_gpu_test_reports/tests_tf_gpu_stats.txt"
            },
            "Torch Single GPU": {
                "common": "run_all_tests_torch_gpu_test_reports/tests_torch_gpu_stats.txt"
            },
            "TF Multi GPU": {
                "common": "run_all_tests_tf_multi_gpu_test_reports/tests_tf_multi_gpu_stats.txt"
            },
            "Torch Multi GPU": {
                "common": "run_all_tests_torch_multi_gpu_test_reports/tests_torch_multi_gpu_stats.txt"
            }
        }

    try:
        results = {}
        for job, file_dict in file_paths.items():
            results[job] = {"failed": 0, "success": 0, "time_spent": ""}
            for key, file_path in file_dict.items():
                with open(file_path) as f:
                    failed, success, time_spent = handle_test_results(f.read())
                    results[job]["failed"] += failed
                    results[job]["success"] += success
                    results[job]["time_spent"] += time_spent[1:-1] + ", "

            results[job]["time_spent"] = results[job]["time_spent"][:-2]
    except Exception as e:
        print(f"Setup error: no artifacts were found. Error: {e}")

    test_results_keys = ["failed", "success"]
    total = {"failed": 0, "success": 0}
    for job, job_result in results.items():
        for result_key in test_results_keys:
            total[result_key] += job_result[result_key]

    url = 'https://hooks.slack.com/services/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'
    headers = {'content-type': 'application/json', 'Accept-Charset': 'UTF-8'}
    r = requests.post(url, data=json.dumps(format_for_slack_with_failures(total, results)), headers=headers)
