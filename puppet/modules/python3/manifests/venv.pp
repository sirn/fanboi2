define python3::venv ($path=$title, $python='python3', $system_site=false) {
  $opts = $system_site ? {
    true    => "--system-site-packages",
    default => undef,
  }

  exec {"python3-venv-install-${title}":
    path    => '/usr/local/bin:/usr/bin:/bin',
    command => "virtualenv -p ${python} ${opts} ${path}",
    require => Exec['python3-install-venv'],
    creates => $path,
  }
}
