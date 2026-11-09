import sys

from converter.registry import DonusturmeHatasi, convert

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Kullanım: python main.py <kaynak> <hedef>")
        sys.exit(1)
    try:
        yazilan = convert(sys.argv[1], sys.argv[2])
    except DonusturmeHatasi as hata:
        print(f"Hata: {hata}", file=sys.stderr)
        sys.exit(1)
    print(f"Dönüşüm tamamlandı: {yazilan}")
