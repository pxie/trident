# trident

The trident of neptune :)

It is the demo app to ingest time series data to Predix TimeSeries database.

## Deploy

### Create services

Since the purpose of this app is to demostrate data ingestion to Predix TimeSeries database, therefore, this app rely on two services on Predix,

1. UAA
2. Predix TimeSeries

If those two services are not created, you need to create them first. Please refer to [Predix TimeSeries setup official doc](https://docs.predix.io/en-US/content/service/data_management/time_series/getting-started-with-the-time-series-service) to create those two services.

**this app depends on service name of two service instances**, the recommandation is,

1. UAA instance name should be `demo-uaa`
2. Predix TimeSeries intance name should be `demo-ts`

### Get source code

1. git clone https://github.com/pxie/trident.git
2. cd trident
3. edit `manifest.yml` file, if your service instances are not named as `demo-uaa`, `demo-ts`
   * replace `demo-uaa` string to your uaa instance name
   * replace `demo-ts` string to your timeseries instance name
4. edit `config.json` file, to fit client id and client secret in your uaa instance
   * replace `client` string to your client id string, for example, your client id is "myclient", the code looks like `"clientid": "myclient",`
   * replace `secret` string to your client secret string, for example, your client secret is "myclientsecret", the code looks like `"clientsecret": "myclientsecret"`
5. cf push. If this command is successful, command line output could be as follows,
```
requested state: started
instances: 1/1
usage: 256M x 1 instances
urls: trident-enoll-nonball.run.aws-jp01-pr.ice.predix.io    <-- your app URL
last uploaded: Wed Jun 28 06:21:21 UTC 2017
stack: cflinuxfs2
buildpack: https://github.com/cloudfoundry/python-buildpack.git

     state     since                    cpu    memory        disk             details
#0   running   2017-06-28 02:22:32 PM   0.0%   80M of 256M   174.6M of 256M
```

## Usage

### Test your configuration

1. access above URL via browser, for example, https://trident-enoll-nonball.run.aws-jp01-pr.ice.predix.io
2. access `/test` path, for example, https://trident-enoll-nonball.run.aws-jp01-pr.ice.predix.io/test
3. if return message is `successfully ingest data.`, your configure are correct.
4. if test failed, you can run `cf logs trident --recent` to retrieve trident logs on predix for trouble-shooting

### Ingest 50,000 data points

1. access `/ingest` path, for example, https://trident-enoll-nonball.run.aws-jp01-pr.ice.predix.io/ingest
2. it will trigger an async process to ingest so many data points
3. you can run `cf logs trident` to retrieve runtime logs on predix to chech whether this task is finished
