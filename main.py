import sys

from converter.registry import convert

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Kullanım: python main.py <kaynak> <hedef>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
    print("Dönüşüm tamamlandı.")