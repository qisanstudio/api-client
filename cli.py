# -*- coding: utf-8 -*-
import click
from subprocess import Popen
from client.client import celery_app, logger, APIClient
from client.esclient import ESAPIClient


@click.group()
def cli():
    pass


@cli.command()
@click.option('--workers', '-w', type=int, help='Number of celery server workers to fire up')
def worker(workers):
    if workers:
        celery_app.conf.update(CELERYD_CONCURRENCY=workers)

    worker = celery_app.Worker(optimization='fair')
    worker.start()


@cli.command()
@click.option( '-p', '--port', default='5555', help='Port on which to start the Flower process')
@click.option('-a', '--address', default='localhost', help='Address on which to run the service')
def flower(port, address):
    BROKER_URL = celery_app.conf.BROKER_URL
    cmd = (
        'celery flower '
        '--broker={BROKER_URL} '
        '--port={port} '
        '--address={address} '
    ).format(**locals())
    logger.info(
        "The 'superset flower' command is deprecated. Please use the 'celery "
        "flower' command instead.")
    logger.info('Starting a Celery Flower instance')
    logger.info(cmd)
    Popen(cmd, shell=True).wait()


@cli.command()
@click.option('--async', '-a', type=bool, help='is async or not')
def test(async):
    client = APIClient('http://localhost:8000')
    headers = {'Authorization': 'Bearer 2808555096_d09e0cdca8fc4af88e7cc47ed055e6f2'}
    data = {'title': '智勇测试client', 'content': 'xxxxxxx'}
    result = client.wechat_service.help_list.post(headers=headers, data=data, is_async=async)
    logger.debug(result)


@cli.command()
@click.option('--async', '-a', type=bool, default=False, help='is async or not')
def es(async):
    client = ESAPIClient('https://search-cia-ykxpgqrde45eke7u2vw72qh6c4.cn-northwest-1.es.amazonaws.com.cn')

    logger.info("insert data")
    data = {
        "user": "zhiyong",
        "post_date": "2018-11-15T14:12:12",
        "message": "智勇的message",
        "as_dict": {
            "title": "我是标题",
            "conent": "我是内容"
        }
    }
    # resp = client.dev_index.bnb_db_backup_type._post(json=data, is_async=async)
    # logger.debug(resp.json())

    logger.info("get index mapping")
    resp = client.dev_index._mapping.bnb_db_backup_type._get(is_async=async)
    logger.debug(resp.json())

    logger.info("filter by post_data")
    search_by_date_json = {
                                "query": {
                                    "range": {
                                        "post_date": {
                                            "gte": "2018-11-14T00:00:00",
                                            "lte": "2018-11-15T15:00:00"
                                        }
                                    }
                                }
                            }
    resp = client.dev_index.bnb_db_backup_type._search._post(json=search_by_date_json, is_async=async)
    logger.debug(resp.json())

    logger.info("filter by post_data and user_id")
    search_by_date_json = {
                              "query": {
                                "bool": {
                                  "must": {
                                    "term": {
                                      "user": "zhiyong"
                                    }
                                  },
                                  "filter": {
                                    "range": {
                                      "post_date": {
                                        "gte": "2018-11-14T00:00:00",
                                        "lte": "2018-11-15T15:00:00"
                                      }
                                    }
                                  }
                                }
                              }
                            }
    resp = client.dev_index.bnb_db_backup_type._search._post(json=search_by_date_json, is_async=async)
    logger.debug(resp.json())


if __name__ == '__main__':
    cli()
