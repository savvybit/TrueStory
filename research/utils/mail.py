import sys

from truestory import mail
from truestory.models import SubscriberModel


def send_mail():
    # Works with SendGrid v5.4.1.
    mail.send_mail("cmin764@gmail.com", "TrueStory", "Salutare Cosmin!")


def send_greetings():
    subscriber = SubscriberModel(mail="cmin764@gmail.com")
    subscriber.send_greetings()


def main():
    if len(sys.argv) != 2:
        print(f"Usage: {sys.argv[0]} FUNC")
        return

    funcs = {
        "send_mail": send_mail,
        "send_greetings": send_greetings,
    }
    funcs[sys.argv[1]]()


if __name__ == "__main__":
    main()


# Example: $ python mail.py send_greetings
