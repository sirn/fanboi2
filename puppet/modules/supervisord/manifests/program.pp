define supervisord::program (
  $command = undef,
  $user    = undef,
  $env     = undef,
  $cwd     = undef,
  $retries = 65535
) {
  $config_dir = '/etc/supervisor/conf.d/'

  file {"${config_dir}${title}.conf":
    ensure  => file,
    owner   => 'root',
    group   => 'root',
    mode    => '0644',
    content => template('supervisord/program.conf.erb'),
    notify  => Service['supervisor'],
  }
}
