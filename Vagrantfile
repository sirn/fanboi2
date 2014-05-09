Vagrant.configure("2") do |config|
  config.vm.box = "precise64"
  config.vm.network :forwarded_port, guest: 80, host: 8080
  config.vm.network :private_network, ip: "192.168.200.100"
  config.vm.synced_folder ".", "/vagrant", type: "nfs"
  config.vm.provision :ansible do |ansible|
    ansible.limit = "all"
    ansible.playbook = "provisioning/site.yml"
    ansible.inventory_path = "provisioning/development_hosts"
  end
end
