execute "apt-get-update and upgrade" do
  command "apt-get update"
  command "apt-get dist-upgrade"
end

package "apache2"
package "libapache2-mod-wsgi"
package "memcached"
package "python-memcache"
package "git-core"
package "python-dev"
package "python-setuptools"
package "python-mysqldb"
package "build-essential"
package "subversion"
package "mercurial"
package "libgraphicsmagick++1-dev"
package "libboost-python1.40-dev"
# package "rabbitmq-server"

template "/etc/apache2/apache2.conf" do
    source "apache2.conf"
    owner "root"
    group "root"
    mode "644"
end
