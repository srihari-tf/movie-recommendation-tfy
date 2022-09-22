import logging

from servicefoundry import Build, Service, PythonBuild, Resources

logging.basicConfig(level=logging.INFO)

image = Build(
    build_spec=PythonBuild(
        command="streamlit run webapp.py --server.port 8080",
        requirements_path="requirements.txt",
    ),
)

env = {
    "TFY_API_KEY": "tfy-secret://user-truefoundry:tfy-api-key:TFY_API_KEY"
}

service = Service(
    name="streamlit-app",
    image=image,
    ports=[{"port": 8080}],
    env=env,
    resources=Resources(cpu_request='0.5', cpu_limit='0.5', memory_limit='1000', memory_request='1000' )
)

deployment = service.deploy(workspace_fqn="v1:tfy-dev-cluster:demo-workspace")