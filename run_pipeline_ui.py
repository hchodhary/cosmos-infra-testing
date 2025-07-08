import os

import requests
import streamlit as st

REPO_CONFIGS = {
    "cosmos-transfer1": {
        "variables": {
            "PR_NUMBER": {
                "description": "Pull request number to be tested in the CI pipeline. If set to -1 (default), the pipeline will run on the 'nvidia-cosmos/cosmos-transfer1' repository and the 'main' branch.",
                "value": "-1",
            },
            "CLONE_METHOD": {
                "description": "Method used to clone the repository",
                "value": "https",
                "options": ["ssh", "https", "https-with-token"],
            },
            "TEST_EXTERNAL_USER_PR": {
                "description": "Set to 'true' to Run tests on external user pull requests",
                "value": "false",
                "options": ["true", "false"],
            },
            "REFRESH_CHECKPOINTS": {
                "description": "Refresh the checkpoints. This will delete the existing checkpoints and download the latest ones.",
                "value": "false",
                "options": ["true", "false"],
            },
        }
    },
    "cosmos-predict1": {"variables": {"DUMMY_VARIABLE1": {"value": "resnet50"}, "DUMMY_VARIABLE2": {"value": "0.5"}}},
    "cosmos-predict2": {
        "variables": {"DUMMY_VARIABLE3": {"value": "fast"}, "DUMMY_VARIABLE4": {"value": "true", "options": ["true", "false"]}}
    },
}

GITLAB_API_URL = "https://gitlab-master.nvidia.com/api/v4/projects/168253/trigger/pipeline"
TRIGGER_TOKEN = os.getenv("GITLAB_TRIGGER_TOKEN")
REF = "hchodhary/feat-create-dynamic-gitlab-ci-page"

st.title("🚀 Trigger GitLab Pipeline")

if not TRIGGER_TOKEN:
    st.error("Environment variable GITLAB_TRIGGER_TOKEN not set.")
    st.stop()

selected_repo = st.selectbox("Select Repository", list(REPO_CONFIGS.keys()))
user_inputs = {}

if selected_repo:
    st.subheader(f"Variables for `{selected_repo}`")
    for var, meta in REPO_CONFIGS[selected_repo]["variables"].items():
        default = meta.get("value", "")
        description = meta.get("description", "")
        options = meta.get("options")

        if options:
            user_inputs[var] = st.selectbox(f"{var}", options, index=options.index(default) if default in options else 0)
        else:
            user_inputs[var] = st.text_input(f"{var}", default)

        if description:
            st.caption(description)

if st.button("🚀 Trigger Pipeline"):
    payload = {
        "token": TRIGGER_TOKEN,
        "ref": REF,
        "variables[REPO_NAME]": selected_repo,
    }

    for key, value in user_inputs.items():
        payload[f"variables[{key}]"] = value

    masked_payload = payload.copy()
    masked_payload["token"] = "****MASKED****"

    with st.expander("Trigger Payload"):
        st.json(masked_payload)

    response = requests.post(GITLAB_API_URL, data=payload)

    if response.status_code == 201:
        pipeline_url = response.json().get("web_url")
        st.success("✅ Pipeline triggered successfully!")
        st.markdown(f"[🔗 View Pipeline]({pipeline_url})")
    else:
        st.error(f"❌ Failed to trigger pipeline: {response.status_code}")
        st.code(response.text)
