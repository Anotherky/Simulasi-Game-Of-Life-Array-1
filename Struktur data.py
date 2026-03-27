# ============================================================
#  Custom Big Number ADT (Modified Version)
#  - Linked List Version
#  - Array/List Version
# ============================================================

# =========================
# LINKED LIST VERSION
# =========================

class DigitNode:
    def __init__(self, value):
        self.value = value
        self.next = None


class BigNumberLinked:
    def __init__(self, number="0"):
        self.head = None
        self.is_negative = False
        self._build_from_string(str(number))

    def _build_from_string(self, text):
        text = text.strip()

        if text.startswith('-'):
            self.is_negative = True
            text = text[1:]
        else:
            self.is_negative = False

        text = text.lstrip('0') or '0'

        for ch in text[::-1]:  # langsung balik
            node = DigitNode(int(ch))
            node.next = self.head
            self.head = node

    def _to_list(self):
        arr = []
        cur = self.head
        while cur:
            arr.append(cur.value)
            cur = cur.next
        return arr

    def _from_list(self, arr, neg=False):
        self.head = None
        for d in arr:
            node = DigitNode(d)
            node.next = self.head
            self.head = node

        self.is_negative = neg if arr != [0] else False

    def __str__(self):
        digits = self._to_list()
        text = ''.join(map(str, digits[::-1]))
        return '-' + text if self.is_negative else text

    # ===== Arithmetic Basic =====
    def _sum(self, a, b):
        res, carry = [], 0
        n = max(len(a), len(b))

        for i in range(n):
            x = a[i] if i < len(a) else 0
            y = b[i] if i < len(b) else 0
            total = x + y + carry

            res.append(total % 10)
            carry = total // 10

        if carry:
            res.append(carry)

        return res

    def _diff(self, a, b):
        res, borrow = [], 0

        for i in range(len(a)):
            x = a[i] - borrow
            y = b[i] if i < len(b) else 0

            if x < y:
                x += 10
                borrow = 1
            else:
                borrow = 0

            res.append(x - y)

        while len(res) > 1 and res[-1] == 0:
            res.pop()

        return res

    def add(self, other):
        a = self._to_list()
        b = other._to_list()

        result = self._sum(a, b)

        obj = BigNumberLinked()
        obj._from_list(result)
        return obj

    def subtract(self, other):
        a = self._to_list()
        b = other._to_list()

        result = self._diff(a, b)

        obj = BigNumberLinked()
        obj._from_list(result)
        return obj

    def multiply(self, other):
        a = self._to_list()
        b = other._to_list()

        res = [0]*(len(a)+len(b))

        for i in range(len(a)):
            carry = 0
            for j in range(len(b)):
                temp = a[i]*b[j] + res[i+j] + carry
                res[i+j] = temp % 10
                carry = temp // 10
            res[i+len(b)] += carry

        while len(res) > 1 and res[-1] == 0:
            res.pop()

        obj = BigNumberLinked()
        obj._from_list(res)
        return obj


# =========================
# ARRAY VERSION
# =========================

class BigNumberArray:
    def __init__(self, value="0"):
        self.neg = False
        value = str(value).strip()

        if value.startswith('-'):
            self.neg = True
            value = value[1:]

        value = value.lstrip('0') or '0'
        self.data = [int(x) for x in value[::-1]]

    def __str__(self):
        s = ''.join(map(str, self.data[::-1]))
        return '-' + s if self.neg else s

    def _add_core(self, a, b):
        res, carry = [], 0
        size = max(len(a), len(b))

        for i in range(size):
            d1 = a[i] if i < len(a) else 0
            d2 = b[i] if i < len(b) else 0

            total = d1 + d2 + carry
            res.append(total % 10)
            carry = total // 10

        if carry:
            res.append(carry)

        return res

    def add(self, other):
        result = self._add_core(self.data, other.data)
        return BigNumberArray(''.join(map(str, result[::-1])))

    def multiply(self, other):
        a, b = self.data, other.data
        res = [0]*(len(a)+len(b))

        for i in range(len(a)):
            carry = 0
            for j in range(len(b)):
                temp = a[i]*b[j] + res[i+j] + carry
                res[i+j] = temp % 10
                carry = temp // 10
            res[i+len(b)] += carry

        while len(res) > 1 and res[-1] == 0:
            res.pop()

        return BigNumberArray(''.join(map(str, res[::-1])))


# =========================
# DEMO TEST (DIUBAH JUGA)
# =========================

if __name__ == "__main__":
    print("=== DEMO CUSTOM BIG NUMBER ===")

    a = BigNumberArray("98765")
    b = BigNumberArray("4321")

    print("\n[ARRAY VERSION]")
    print("a =", a)
    print("b =", b)
    print("a + b =", a.add(b))
    print("a * b =", a.multiply(b))

    x = BigNumberLinked("55555")
    y = BigNumberLinked("1111")

    print("\n[LINKED LIST VERSION]")
    print("x =", x)
    print("y =", y)
    print("x + y =", x.add(y))
    print("x * y =", x.multiply(y))