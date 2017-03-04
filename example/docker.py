from simplekit.docker import factory


def main():
    client = factory.get('scdfis01')
    # client.update_image_2('testing', 'docker.neg/dfis/biz_event_cassandra:0.0.1.release8.baa85')
    result = client.create_container('benjamin', 'docker.neg/dfis/biz_event_cassandra:0.0.1.release8.baa85',
                                     restartpolicy='no',
                            env=['HELLO=BENJAMIN'], command='/bin/sh -c "env"')
    print(result)


if __name__ == '__main__':
    main()
