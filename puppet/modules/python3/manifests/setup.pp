define python3::setup (
  $setup  = undef,
  $mode   = 'install',
  $python = 'python3',
  $venv   = undef,
  $user   = undef
) {
  exec {"python3-setup-${title}":
    path        => "${venv}/bin:/usr/local/bin:/usr/bin:/bin",
    command     => "${python} ${setup} ${mode}",
    environment => ['LANG=en_US.UTF-8'], # Fix Unicode error with Python 3.
    unless      => "${python} -c 'import ${title}'",
    cwd         => "/tmp/",
    user        => $user,
    timeout     => 0,
  }
}
