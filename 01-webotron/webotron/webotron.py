import boto3
import click
from pathlib import Path
import mimetypes

session = boto3.Session(profile_name='pythonautomation')
s3 = session.resource('s3')

@click.group()
def cli():
    "webotron deploys websites to AWS"
    pass

@cli.command('list-buckets')
def list_buckets():
    "list all buckets"
    for buckets in s3.buckets.all():
        print(buckets)

@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    "list objects in an S3 bucket"
    for obj in s3.Bucket(bucket).objects.all():
        print(obj)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    "Create and configure S3 bucket"
    new_bucket = s3.create_bucket(Bucket=bucket)


    policy= """
    {
      "Version":"2012-10-17",
      "Statement":[{
      "Sid":"PublicReadGetObject",
      "Effect":"Allow",
      "Principal": "*",
          "Action":["s3:GetObject"],
          "Resource":["arn:aws:s3:::%s/*"
          ]
        }
      ]
    }
    """ % new_bucket.name
    policy = policy.strip()

    pol = new_bucket.Policy()
    pol.put(Policy=policy)

    website = new_bucket.Website()
    website.put(WebsiteConfiguration={'ErrorDocument': {
            'Key': 'error.html'
        },
        'IndexDocument': {
            'Suffix': 'index.html'
        }
    })

    return

def upload_file(s3_bucket, path, key):
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
    path,
    key,
    ExtraArgs={
    'ContentType': 'text/html'
    })

@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    "Sync contents of PATHNAME to bucket"
    s3_bucket = s3.Bucket(bucket)

    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for p in target.iterdir():
            if p.is_dir(): handle_directory(p)
            if p.is_file(): upload_file(s3_bucket, str(p), str(p.relative_to(root)))

    handle_directory(root)

if __name__ == '__main__':
    cli()
