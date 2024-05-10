from django.db import models

# Create your models here.
class Pages(models.Model):
    title = models.CharField(max_length=100)
    url = models.URLField(max_length=200)
    last_modification_date = models.DateTimeField()
    page_size = models.IntegerField()
    child_link_list = models.TextField()

    def __str__(self):
        # return every field of the model
        return f"{self.title}, {self.url}, {self.last_modification_date}, {self.page_size}, {self.child_link_list}"
    
class Keywords(models.Model):
    keyword = models.CharField(max_length=50)

    def __str__(self):
        return self.keyword
    
class Indexer(models.Model):
    page_id = models.ForeignKey(Pages, on_delete=models.CASCADE)
    keyword_id = models.ForeignKey(Keywords, on_delete=models.CASCADE)
    frequency = models.IntegerField()
    is_title = models.BooleanField()

    def __str__(self):
        return f"{self.page_id}, {self.keyword_id}, {self.frequency}"
    
class TopKeywords(models.Model):
    page_id = models.ForeignKey(Pages, on_delete=models.CASCADE)
    keyword_id = models.ForeignKey(Keywords, on_delete=models.CASCADE)
    frequency = models.IntegerField()
    rank = models.IntegerField()

    class Meta:
        unique_together = ('page_id', 'rank')

    def __str__(self):
        return f"{self.page_id}, {self.keyword_id}, {self.frequency}, {self.rank}"

