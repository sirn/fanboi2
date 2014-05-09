Vagrant.configure("2") do |config|
  config.vm.box = "precise64"
  config.vm.network :forwarded_port, :guest => 80, :host => 8080
  config.vm.network :private_network, :ip => '192.168.200.100'
  config.vm.provision :ansible do |ansible|
    ansible.limit = "all" # https://github.com/mitchellh/vagrant/issues/3096
    ansible.playbook = "provisioning/site.yml"
    ansible.inventory_path = "provisioning/development_hosts"
  end
end
