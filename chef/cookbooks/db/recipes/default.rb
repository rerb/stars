execute "apt-get-update" do
  command "apt-get update"
end

package "rabbitmq-server"
package "mysql-server"