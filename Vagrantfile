# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.define "web", primary: true do |web|
    web.vm.box = "generic/freebsd11"
    web.vm.network "private_network", ip: "10.200.80.100"
    web.vm.network "forwarded_port", guest: 6543, host: 6543
    web.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ["actimeo=2"]
    web.ssh.shell = "sh"
    web.vm.provision :shell, privileged: true, path: "vendor/vagrant/bootstrap_web.sh"
  end

  # The builder vm is for building Docker image in case you're not a fan of Docker.
  # By default it's not created when running `vagrant up`.
  # To use it, explicitly run `vagrant up builder`.
  config.vm.define "builder", autostart: false do |builder|
    builder.vm.box = "generic/debian9"
    builder.vm.network "private_network", ip: "10.200.80.101"
    builder.vm.synced_folder ".", "/vagrant", type: "nfs", mount_options: ["actimeo=2"]
    builder.vm.provision :shell, privileged: true, path: "vendor/vagrant/bootstrap_builder.sh"
  end
end
