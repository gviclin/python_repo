from django.db import models
from django.utils import timezone


class User(models.Model):
	# Fields
	django_user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
	user_id = models.IntegerField(primary_key=True)
	firstname = models.CharField(max_length=50)
	lastname = models.CharField(max_length=50)
	weight = models.FloatField(null=True)
	sex = models.CharField(max_length=50)
	country = models.CharField(max_length=50)
	state = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	follower_count = models.IntegerField(null=True)
	friend_count = models.IntegerField(null=True)
	measurement_preference = models.CharField(max_length=50)
	ftp = models.IntegerField(null=True)
	
	updated_date = models.DateTimeField(
		default=timezone.now)
			
	strava_creation_date = models.DateTimeField(
		blank=True, null=True)
			
	first_activity_date = models.DateTimeField(
		blank=True, null=True)
			
	last_activity_date = models.DateTimeField(
		blank=True, null=True)
		
	act_number = models.IntegerField(null=True)
	
	year_run_objective = models.IntegerField()
	year_ride_objective = models.IntegerField()
		
	# Metadata
	class Meta: 
		ordering = ['-user_id']
	
	def publish(self):
		self.published_date = timezone.now()
		self.save()

	def __str__(self):
		#String for representing the MyModelName object (in Admin site etc.).
		return self.firstname + " " + self.lastname
