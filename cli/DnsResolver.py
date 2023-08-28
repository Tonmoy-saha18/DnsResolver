import socket
from Cache import *

dns_server = "8.8.8.8"
dns_port = 53


def construct_dns_query(domain_name):
    query_id = 12345  # Choose a query ID
    query = bytearray()

    # Add query header
    query += query_id.to_bytes(2, byteorder="big")
    query += int("0100", 16).to_bytes(2, byteorder="big")  # Standard query
    query += int("0001", 16).to_bytes(2, byteorder="big")  # Number of questions
    query += int("0000", 16).to_bytes(2, byteorder="big")  # Number of answers
    query += int("0000", 16).to_bytes(2, byteorder="big")  # Number of authority records
    query += int("0000", 16).to_bytes(2, byteorder="big")  # Number of additional records

    # Add domain name to query
    for part in domain_name.split("."):
        query += len(part).to_bytes(1, byteorder="big")
        query += part.encode()

    query += b"\x00"  # Null-terminator

    # Add query type and class (A record and Internet class)
    query += int("0001", 16).to_bytes(2, byteorder="big")  # Query type (A record)
    query += int("0001", 16).to_bytes(2, byteorder="big")  # Query class (Internet class)

    return query


def resolve_dns(domain_name):
    query = construct_dns_query(domain_name)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.sendto(query, (dns_server, dns_port))
        response, _ = s.recvfrom(1024)

    return response


def isValidResponse(response):
    rcode_value = str(response)[10:12]
    return rcode_value == '80'


def parse_dns_response(response):
    if isValidResponse(response):
        ip_address_array = []
        # Skip header bytes
        response = response[12:]

        # Skip QNAME (query domain name)
        while response[0] != 0:
            length = response[0]
            response = response[length + 1:]

        # Skip QTYPE and QCLASS fields and other fields
        response = response[7:]

        # Skipping type of records, internet class , ttl values, and ip address size
        response = response[10:]

        # Extract the IP address (4 bytes)
        while len(response) > 0:
            try:
                ip_address = ".".join(str(byte) for byte in response[:4])
                ip_address_array.append(ip_address)
                response = response[16:]
            except Exception as e:
                print(e)
                break
        return ip_address_array
    return None


def dns_resolver(domain_name):
    try:
        query = construct_dns_query(domain_name)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.sendto(query, (dns_server, dns_port))
            response, _ = s.recvfrom(1024)

        ip_addresses = parse_dns_response(response)
        return ip_addresses

    except (socket.timeout, socket.error) as e:
        return f"DNS resolution error: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"


if __name__ == "__main__":
    cache = Cache(max_size=5)
    while True:
        domain_name = input("Enter domain name: ")
        if domain_name == 'break':
            break
        if cache.get(domain_name):
            print("From cache\n______________")
            print(f"Ip addresses for domain name {domain_name} are :{cache.get(domain_name)}")
        else:
            ip_addresses = dns_resolver(domain_name)
            cache.set(domain_name, ip_addresses)
            if ip_addresses:
                for ip_address in ip_addresses:
                    print(f"IP address of {domain_name} are: {ip_address}")
            else:
                print(f"Your domain name {domain_name} is incorrect. We can't find its ip address")
