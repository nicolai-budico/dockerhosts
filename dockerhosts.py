#!/usr/bin/python3

"""
dockerhosts service implementation
"""

from subprocess import Popen
from subprocess import PIPE
import threading
import json
import os
import shutil

import signal
import time


DOCKERHOSTS_CONF_JSON = "/etc/dockerhosts.conf.json"

class DockerHostsService:
    """Service implementation"""

    class Config:
        """Service configuration"""
        def __init__(self):
            self.hosts_folder: str
            self.docker_executable: str
            self.dnsmasq_executable: str
            self.dnsmasq_parameters: list

            conf_data: dict

            if os.path.exists(DOCKERHOSTS_CONF_JSON):
                with open(DOCKERHOSTS_CONF_JSON, "r") as stream:
                    conf_data = json.load(stream)
            else:
                conf_data = dict()

            self.hosts_folder = conf_data.get("hosts-folder", "/var/run/docker-hosts")
            self.docker_executable = conf_data.get("docker-executable", "/usr/bin/docker")
            self.dnsmasq_executable = conf_data.get("dnsmasq-executable", "/usr/sbin/dnsmasq")
            self.dnsmasq_parameters = conf_data.get("dnsmasq-parameters", [
                "--no-daemon",
                "--clear-on-reload",
                "--no-resolv",
                "--no-hosts",
                "--listen-address=127.0.0.54",
                "--port=53"
            ])

    def __init__(self):
        self.config = DockerHostsService.Config()

        self.dnsmasq_process: Popen
        self.dnsmasq_process = None

        self.containers_thread: threading.Thread
        self.containers_thread = None
        self.stopping = False

        self.previous_containers = None

        if not os.path.exists(self.config.hosts_folder):
            os.makedirs(self.config.hosts_folder)

        signal.signal(signal.SIGINT, self.stop)
        signal.signal(signal.SIGTERM, self.stop)

    def stop(self, _signum, _frame):
        """Stops threads and cleanup resources"""
        print("Stop signal received.")
        self.stopping = True

        # Stop dnsmasq thread
        if (self.dnsmasq_process is not None) and (self.dnsmasq_process.poll() is not None):
            print("Stopping dnsmasq.")
            self.dnsmasq_process.send_signal(signal.SIGKILL)
            self.dnsmasq_process.kill()
            self.dnsmasq_process.wait()
            print("Dnsmasq exited.")

        # Stop containers listener
        if not self.containers_thread is None:
            self.containers_thread.join()

        # Remove temporary folder
        if os.path.exists(self.config.hosts_folder):
            shutil.rmtree(self.config.hosts_folder)

    def start(self):
        """Run service"""
        # Start containers thread
        self.containers_thread = threading.Thread(target=self.update_hosts_file)
        self.containers_thread.start()

        # Start dnsmasq process
        self.dnsmasq_process = self.start_dnsmasq()

        try:
            self.dnsmasq_process.wait()
        except KeyboardInterrupt:
            self.stop(None, None)

    def start_dnsmasq(self) -> Popen:
        """ Start dnsmasq process """
        args = []
        args.append(self.config.dnsmasq_executable)
        args.extend(self.config.dnsmasq_parameters)
        args.append("--hostsdir=%s" % self.config.hosts_folder)

        process = Popen(shell=True, stdout=PIPE, args=" ".join(args))
        return process

    def get_running_containers(self) -> list:
        """ Returns list of running containers """
        container_ids: list
        command = self.config.docker_executable + " ps -q"
        popen = Popen(command, shell=True, stdout=PIPE)
        with popen.stdout as stream:
            container_ids = stream.read().decode('utf8') \
                .strip() \
                .split("\n")
        container_ids = [c.strip() for c in container_ids if c]
        container_ids.sort()
        return container_ids

    def inspect_containers(self, container_ids: list) -> list:
        """ Returns containers information """
        command = self.config.docker_executable + " inspect " + " ".join(container_ids)
        popen = Popen(command, shell=True, stdout=PIPE)
        with popen.stdout as stream:
            containers = json.load(stream)

        return containers

    def update_hosts_file(self):
        """Writes hosts file into temporary folder"""
        while not self.stopping:
            container_ids = self.get_running_containers()

            if self.previous_containers != container_ids:
                self.previous_containers = container_ids

                filename = self.config.hosts_folder + "/hosts"
                lines = ["#  " + filename]

                if container_ids:
                    print("Running containers: " + " ".join(container_ids))
                    containers_data = self.inspect_containers(container_ids)

                    for container in containers_data:
                        hostname = ".".join([
                            container["Config"]["Hostname"],
                            container["Config"]["Domainname"]
                        ])
                        networks = list(container["NetworkSettings"]["Networks"].values())
                        hostaddr = networks[0]["IPAddress"]
                        lines.append(hostaddr + "\t" + hostname)

                with open(filename, 'w') as the_file:
                    the_file.write("\n".join(lines) + "\n")

            for _ in range(1, 20):
                time.sleep(0.1)
                if self.stopping:
                    break


def main():
    """Main method"""
    service = DockerHostsService()
    service.start()


main()
