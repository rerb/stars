# STARS Web Application Server

execute "apt-get-update" do
  command "apt-get update"
  # command "apt-get dist-upgrade"
end

# Base packages

package "memcached"
package "python-memcache"
package "git-core"
package "python-dev"
package "python-setuptools"
package "python-mysqldb"
package "build-essential"
package "subversion"
package "libgraphicsmagick++1-dev"
package "libboost-python1.40-dev"
package "mercurial"

include_recipe "mysql::client"

# Python Packages

include_recipe "python"

# Kept timing out :(
# python_pip "mercurial" do
#   action :install
# end