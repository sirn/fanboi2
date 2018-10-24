# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "generic/freebsd11"

  config.vm.network "private_network", ip: "10.200.80.100"
  config.vm.network "forwarded_port", guest: 6543, host: 6543
  config.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ["actimeo=2"]
  config.ssh.shell = "sh"

  config.vm.provision :shell, privileged: true, path: "vendor/vagrant_system.sh"
  config.vm.provision :shell, privileged: false, path: "vendor/vagrant_user.sh"
end
