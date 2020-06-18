from django.db import models
from django.utils import timezone


class User(models.Model):
	# Fields
	django_user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
	user_id = models.IntegerField(primary_key=True)
	firstname = models.CharField(max_length=50)
	lastname = models.CharField(max_length=50)
	weight = models.FloatField()
	sex = models.CharField(max_length=50)
	country = models.CharField(max_length=50)
	state = models.CharField(max_length=50)
	city = models.CharField(max_length=50)
	follower_count = models.IntegerField()
	friend_count = models.IntegerField()
	measurement_preference = models.CharField(max_length=50)
	ftp = models.IntegerField()
	
	created_date = models.DateTimeField(
		default=timezone.now)
			
	strava_creation_date = models.DateTimeField(
		blank=True, null=True)
			
	first_activity_date = models.DateTimeField(
		blank=True, null=True)
			
	last_activity_date = models.DateTimeField(
		blank=True, null=True)
		
	# Metadata
	class Meta: 
		ordering = ['-user_id']
	
	def publish(self):
		self.published_date = timezone.now()
		self.save()

	def __str__(self):
		#String for representing the MyModelName object (in Admin site etc.).
		return self.firstname + " " + self.lastname
