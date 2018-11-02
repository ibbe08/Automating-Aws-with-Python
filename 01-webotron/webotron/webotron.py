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


import boto3
import click

from bucket import BucketManager


session = boto3.Session(profile_name='pythonautomation')
bucket_manager = BucketManager(session)


@click.group()
def cli():
    """Webotron deploys websites to AWS."""
    pass


@cli.command('list-buckets')
def list_buckets():
    """List all s3 buckets."""
    for buckets in bucket_manager.all_buckets():
        print(buckets)


@cli.command('list-bucket-objects')
@click.argument('bucket')
def list_bucket_objects(bucket):
    """List objects in an S3 bucket."""
    for obj in bucket_manager.all_objects(bucket):

        print(obj)

@cli.command('setup-bucket')
@click.argument('bucket')
def setup_bucket(bucket):
    """Create and Configure S3 bucket."""
    new_bucket = bucket_manager.init_bucket(bucket)
    bucket_manager.set_policy(new_bucket)
    bucket_manager.configure_website(new_bucket)

    return

@cli.command('sync')
@click.argument('pathname', type=click.Path(exists=True))
@click.argument('bucket')
def sync(pathname, bucket):
    """Sync contents of PATHNAME to bucket."""
    bucket_manager.sync(pathname, bucket)


if __name__ == '__main__':
    cli()
