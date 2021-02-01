curl localhost:5002/user/create -H "Content-Type: application/json" -d @user3.json
curl localhost:5002/role/create  -H "Content-Type: application/json" -d @role1.json
curl localhost:5002/role/create -H "Content-Type: application/json" -d @role2.json
curl localhost:5002/user/create -H "Content-Type: application/json" -d @user1.json
curl localhost:5002/user/create -H "Content-Type: application/json" -d @user2.json
curl localhost:5003/permissions/exampleUser
curl localhost:5004/admin -H "Cookie: username=exampleUser"
