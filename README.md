<h1>CC-Project-DBaaS</h1>

<h2> Architecture</h2>
<img src="Report/DBaaS_Architecture.jpg" height=500></img>
<p><b>Note:</b> Please read the <a href="https://github.com/kirthikagurumurthy/Rideshare-Application---DBaaS/blob/master/Report/ReportTemplateCloudComputing.docx">report</a> for a better insight on the architecture.</p>

<h2> Instructions to run the code</h2>
<h3> Rides Instance </h3>
1. Start the AWS Rides Instance<br>
2. <code>cd rides-test/rides</code><br>
3. <code>sudo docker system prune --volumes</code><br>
4. <code>sudo docker-compose up --build</code><br>

<h3> Users Instance</h3>
1. Start the AWS Users Instance<br>
2. <code>cd users-test/users</code><br>
3. <code>sudo docker system prune --volumes</code><br>
4. <code>sudo docker-compose up --build</code><br>

<h3> DBaaS Instance</h3>
1. Start the AWS DBaaS Instance<br>
2. <code>cd project-test/project</code><br>
3. <code>sudo docker rm -f $(sudo docker ps -aq)</code><br>
4. <code>sudo docker system prune --volumes</code><br>
5. <code>sudo docker-compose up --build</code><br>
