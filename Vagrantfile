Vagrant.configure("2") do |config|
  config.vm.box = "precise64"
  config.vm.network :forwarded_port, :guest => 6543, :host => 6543
  config.vm.network :forwarded_port, :guest => 9001, :host => 9001
  config.vm.provision :puppet do |puppet|
    puppet.module_path    = "puppet/modules"
    puppet.manifests_path = "puppet/manifests"
    puppet.manifest_file  = "site.pp"
  end
end
