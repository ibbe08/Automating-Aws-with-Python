#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Webotron: Deploy websites to AWS.

Webotron automates the process of deploying static websites to AWS.
- Configure AWS s3 buckets.
    - Create buckets
    - Set buckets for static website hosting
    - Deploy local files to buckets
- Configure DNS with AWS Route 53.
- Configure a Content Delivery Network with AWS and Cloudfront.
"""

from pathlib import Path
import mimetypes
import boto3
import click


session = boto3.Session(profile_name='pythonautomation')
s3 = session.resource('s3')


@click.group()
def cli():
    """Webotron deploys websites to AWS."""
    pass


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for buckets in s3.buckets.all():
        print(buckets)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in an S3 bucket."""
    for obj in s3.Bucket(bucket).objects.all():

        print(obj)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and Configure S3 bucket."""
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
    """Upload path to s3_bucket at key."""
    content_type = mimetypes.guess_type(key)[0] or 'text/plain'
    s3_bucket.upload_file(
    path,
    key,
    ExtraArgs={
    'ContentType': content_type
    })

@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync contents of PATHNAME to bucket."""
    s3_bucket = s3.Bucket(bucket)

    root = Path(pathname).expanduser().resolve()

    def handle_directory(target):
        for path in target.iterdir():
            if path.is_dir():
                handle_directory(path)
            if path.is_file():
                upload_file(s3_bucket, str(path), str(path.relative_to(root)))


    handle_directory(root)

if __name__ == '__main__':
    cli()
