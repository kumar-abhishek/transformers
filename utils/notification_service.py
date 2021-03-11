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

import sys


def handle_test_results(test_results):
    expressions = test_results.split(" ")

    failures = 0
    success = 0
    time_spent = expressions[-2]

    for i, expression in enumerate(expressions):
        if "failed" in expression:
            failures += int(expressions[i - 1])
        if "passed" in expression:
            success += int(expressions[i - 1])

    if failures:
        print(f"❌ There were some failures: {failures} tests failed. Suite ran for {time_spent[1:-1]}.")
    else:
        print(f"✔️ There were no failures! Suite ran for {time_spent[1:-1]}.")


if __name__ == "__main__":
    handle_test_results(sys.argv[1])
