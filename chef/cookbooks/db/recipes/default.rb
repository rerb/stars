execute "apt-get-update" do
  command "apt-get update"
end

include_recipe "mysql::server"

include_recipe "mysql::client"