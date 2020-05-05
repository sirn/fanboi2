# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
    config.vm.box = "generic/freebsd12"
    config.vm.network "forwarded_port", guest: 6543, host: 6543
    config.ssh.shell = "sh"

    config.vm.provision :shell, privileged: true, path: "vendor/vagrant/setup_sys.sh"
    config.vm.provision :shell, privileged: false, path: "vendor/vagrant/setup_user.sh"

    config.vm.provider :libvirt do |v|
        v.cpus = 2
        v.memory = 2048
    end

    config.vm.provider :virtualbox do |v|
        v.cpus = 2
        v.memory = 2048
    end

    config.vm.provider :vmware_desktop do |v|
        v.vmx["numvcpus"] = "2"
        v.vmx["memsize"] = "2048"
    end
end
