node default {
  Exec {path => ['/usr/local/bin', '/usr/bin', '/bin']}

  # Update only if PostgreSQL is not installed. Psql requires updating APT.
  exec {"apt-update":
    command => 'apt-get update',
    unless  => 'which psql',
    timeout => 0,
  }

  # Run apt before all installations via apt.
  Exec["apt-update"] -> Package <| |>

  # Runtime requirements (database, assets compiler, etc.)
  class {'redis':}
  class {'nodejs': node_ver => 'v0.10.0'}
  class {'postgresql::server':}
  class {'postgresql::devel':}
  class {'python3':}

  # Setup database for development environment and test environment.
  postgresql::db {'fanboi2_dev':  user => 'fanboi2', password => 'dev'}
  postgresql::db {'fanboi2_test': user => 'fanboi2', password => 'dev'}

  # Assets packages and ensure they're installed after NodeJS.
  package {'yui-compressor': ensure => installed}
  package {['stylus', 'nib', 'uglify-js', 'requirejs']:
    ensure   => present,
    provider => 'npm',
    require  => Class['nodejs'],
  }

  # Setup Python virtual environment.
  python3::venv {'fanboi2':
    path        => '/usr/local/venv/fanboi2/',
    python      => 'python3',
    user        => 'vagrant',
    system_site => true,
  }

  # Setup project as development mode (i.e. python setup.py develop).
  python3::setup {'fanboi2':
    mode     => 'develop',
    setup    => '/vagrant/setup.py',
    venv     => '/usr/local/venv/fanboi2/',
    user     => 'vagrant',
    require  => [Python3::Venv['fanboi2'], Class['postgresql::server']],
  }

}
