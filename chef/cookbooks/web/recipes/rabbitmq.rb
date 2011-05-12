package "rabbitmq-server" do
    :upgrade
end

# Configure Rabbitmq for localhost
begin
  execute "add rabbitmq user" do
    command "rabbitmqctl add_user starsapp starsappP122a"
  end
rescue Exception=>e
  print "CREATE FAILED"
end

# begin
#   execute "add rabbitmq vhost" do
#     command "rabbitmqctl add_vhost starsapp"
#   end
# rescue
#   print "Vhost Create Failed (Maybe it exists?)"
# end
# 
# execute "setup rabbitmq permissions" do
#   command "rabbitmqctl set_permissions -p starsapp starsapp \".*\" \".*\" \".*\""
# end