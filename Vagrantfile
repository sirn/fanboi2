# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "pxfs/freebsd-10.3"
  config.vm.network :forwarded_port, :guest => 6543, :host => 6543
  config.ssh.shell = "sh"

  config.vm.provision :shell, :privileged => true, :inline => <<-EOF
    pkg install -y ca_root_nss
    pkg install -y git-lite
    pkg install -y postgresql95-server
    pkg install -y node npm
    pkg install -y redis
    pkg install -y memcached
    pkg install -y bzip2 sqlite3
    pkg install -y python35

    sysrc postgresql_enable=YES
    sysrc redis_enable=YES
    sysrc memcached_enable=YES

    service postgresql initdb
    service postgresql start
    service redis start
    service memcached start

    sudo -u pgsql createuser -ds vagrant || true
    sudo -u pgsql createuser -ds fanboi2 || true
    sh -c 'echo "local all all trust" > /usr/local/pgsql/data/pg_hba.conf'
    sh -c 'echo "host all all 127.0.0.1/32 trust" >> /usr/local/pgsql/data/pg_hba.conf'
    sh -c 'echo "host all all ::1/128 trust" >> /usr/local/pgsql/data/pg_hba.conf'
    service postgresql restart

    fetch -o - https://bootstrap.pypa.io/get-pip.py | /usr/local/bin/python3.5 -
    /usr/local/bin/pip3.5 install virtualenv
  EOF

  config.vm.provision :shell, :privileged => false, :inline => <<-EOF
    virtualenv -p python3.5 $HOME/python3.5

    npm config set prefix $HOME/nodejs
    npm install -g gulp
    npm install -g typings

    echo 'EDITOR=vi; export EDITOR' > $HOME/.profile
    echo 'PAGER=more; export PAGER' >> $HOME/.profile
    echo 'ENV=$HOME/.shrc; export ENV' >> $HOME/.profile
    echo 'PATH="$HOME/nodejs/bin:$HOME/python3.5/bin:$HOME/bin:$PATH"; export PATH' >> $HOME/.profile

    psql template1 -c "CREATE DATABASE fanboi2_development;"
    psql template1 -c "CREATE DATABASE fanboi2_test;"

    cd /vagrant
    cp examples/development.ini.sample development.ini
    cp examples/alembic.ini.sample alembic.ini

    $HOME/python3.5/bin/pip3 install -e .
    $HOME/python3.5/bin/alembic upgrade head

    npm install --no-bin-link
    $HOME/nodejs/bin/typings install
    $HOME/nodejs/bin/gulp
  EOF
end
