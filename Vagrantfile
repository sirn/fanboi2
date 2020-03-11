# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "generic/freebsd12"
    config.vm.network "forwarded_port", guest: 6543, host: 6543
    config.ssh.shell = "sh"
    config.vm.provision :shell, privileged: true, path: "vendor/vagrant/bootstrap.sh"
end
