from glob import glob
from setuptools import setup

package_name = "swarm_aggregation"

setup(
    name=package_name,
    version="0.1.0",
    packages=[package_name],
    data_files=[
        ("share/ament_index/resource_index/packages", [f"resource/{package_name}"]),
        (f"share/{package_name}", ["package.xml"]),
        (f"share/{package_name}/launch", glob("launch/*.launch.py")),
        (f"share/{package_name}/worlds", glob("worlds/*.world")),
    ],
    install_requires=["setuptools"],
    zip_safe=True,
    maintainer="Salmane",
    maintainer_email="salmane@example.com",
    description="TP7 BEECLUST-style decentralized aggregation for TurtleBot3 swarms.",
    license="Apache-2.0",
    entry_points={
        "console_scripts": [
            "aggregation_robot = swarm_aggregation.aggregation_robot:main",
            "supervisor = swarm_aggregation.supervisor:main",
            "plot_sigma2 = swarm_aggregation.plot_sigma2:main",
            "analyze_sigma2 = swarm_aggregation.analyze_sigma2:main",
            "plot_tconv = swarm_aggregation.plot_tconv:main",
        ],
    },
)
