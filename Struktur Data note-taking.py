"""
Struktur Data untuk Aplikasi Note-Taking
- Multiple tags per note (multi-linked by tag)
- Chronological dan alphabetical views (doubly linked sorted)
- Sync status tracking (circular buffer for recent changes)
"""

from datetime import datetime


# ─────────────────────────────────────────────
# 1. NODE & NOTE
# ─────────────────────────────────────────────

class Note:
    def __init__(self, note_id: int, title: str, content: str):
        self.note_id   = note_id
        self.title     = title
        self.content   = content
        self.created_at = datetime.now()
        self.tags: list[str] = []          # daftar tag yang dimiliki note ini

    def __repr__(self):
        return f"Note(id={self.note_id}, title='{self.title}', tags={self.tags})"


# ─────────────────────────────────────────────
# 2. MULTI-LINKED LIST BY TAG
#    Setiap tag punya linked-list sendiri yang
#    menghubungkan semua note dengan tag tersebut.
# ─────────────────────────────────────────────

class TagNode:
    """Node dalam linked list milik sebuah tag."""
    def __init__(self, note: Note):
        self.note = note
        self.next: "TagNode | None" = None


class TagLinkedList:
    """Linked list semua note yang punya tag tertentu."""
    def __init__(self, tag: str):
        self.tag  = tag
        self.head: TagNode | None = None
        self.size = 0

    def add(self, note: Note):
        new_node = TagNode(note)
        new_node.next = self.head
        self.head = new_node
        self.size += 1

    def remove(self, note_id: int):
        prev, curr = None, self.head
        while curr:
            if curr.note.note_id == note_id:
                if prev:
                    prev.next = curr.next
                else:
                    self.head = curr.next
                self.size -= 1
                return True
            prev, curr = curr, curr.next
        return False

    def get_all(self) -> list[Note]:
        result, curr = [], self.head
        while curr:
            result.append(curr.note)
            curr = curr.next
        return result

    def __repr__(self):
        notes = [n.title for n in self.get_all()]
        return f"Tag('{self.tag}') → {notes}"


class MultiTagIndex:
    """
    Index tag → TagLinkedList.
    Satu note bisa masuk ke banyak linked list (multi-linked by tag).
    """
    def __init__(self):
        self._index: dict[str, TagLinkedList] = {}

    def add_note_tag(self, note: Note, tag: str):
        if tag not in note.tags:
            note.tags.append(tag)
        if tag not in self._index:
            self._index[tag] = TagLinkedList(tag)
        self._index[tag].add(note)

    def remove_note_tag(self, note: Note, tag: str):
        if tag in note.tags:
            note.tags.remove(tag)
        if tag in self._index:
            self._index[tag].remove(note.note_id)

    def get_notes_by_tag(self, tag: str) -> list[Note]:
        if tag not in self._index:
            return []
        return self._index[tag].get_all()

    def get_all_tags(self) -> list[str]:
        return list(self._index.keys())

    def __repr__(self):
        return "\n".join(str(ll) for ll in self._index.values())


# ─────────────────────────────────────────────
# 3. DOUBLY LINKED SORTED LIST
#    Dua list terpisah: by date & by title.
# ─────────────────────────────────────────────

class DNode:
    """Node doubly linked list."""
    def __init__(self, note: Note):
        self.note = note
        self.prev: "DNode | None" = None
        self.next: "DNode | None" = None


class SortedDoublyLinkedList:
    """
    Doubly linked list yang selalu terurut.
    key_fn  : fungsi untuk mengambil nilai sort dari Note
    reverse : True = descending
    """
    def __init__(self, key_fn, reverse: bool = False):
        self.head:   DNode | None = None
        self.tail:   DNode | None = None
        self.key_fn  = key_fn
        self.reverse = reverse
        self.size    = 0

    def _should_be_before(self, a: Note, b: Note) -> bool:
        ka, kb = self.key_fn(a), self.key_fn(b)
        return ka > kb if self.reverse else ka < kb

    def insert(self, note: Note):
        new_node = DNode(note)
        # list kosong
        if not self.head:
            self.head = self.tail = new_node
            self.size += 1
            return
        # insert di awal
        if self._should_be_before(note, self.head.note):
            new_node.next = self.head
            self.head.prev = new_node
            self.head = new_node
            self.size += 1
            return
        # cari posisi
        curr = self.head
        while curr.next and not self._should_be_before(note, curr.next.note):
            curr = curr.next
        new_node.next = curr.next
        new_node.prev = curr
        if curr.next:
            curr.next.prev = new_node
        else:
            self.tail = new_node
        curr.next = new_node
        self.size += 1

    def remove(self, note_id: int):
        curr = self.head
        while curr:
            if curr.note.note_id == note_id:
                if curr.prev: curr.prev.next = curr.next
                else:         self.head      = curr.next
                if curr.next: curr.next.prev = curr.prev
                else:         self.tail      = curr.prev
                self.size -= 1
                return True
            curr = curr.next
        return False

    def to_list(self) -> list[Note]:
        result, curr = [], self.head
        while curr:
            result.append(curr.note)
            curr = curr.next
        return result

    def __repr__(self):
        return " <-> ".join(n.title for n in self.to_list())


# ─────────────────────────────────────────────
# 4. CIRCULAR BUFFER – SYNC STATUS TRACKING
#    Menyimpan N perubahan terakhir secara efisien.
# ─────────────────────────────────────────────

class SyncEvent:
    def __init__(self, note_id: int, action: str):
        self.note_id   = note_id
        self.action    = action          # "CREATE", "UPDATE", "DELETE"
        self.timestamp = datetime.now()
        self.synced    = False

    def __repr__(self):
        status = "✓" if self.synced else "✗"
        return f"[{status}] {self.action} note#{self.note_id} @ {self.timestamp.strftime('%H:%M:%S')}"


class CircularSyncBuffer:
    """
    Circular buffer kapasitas tetap untuk melacak perubahan terkini.
    Otomatis menimpa event terlama saat buffer penuh.
    """
    def __init__(self, capacity: int = 10):
        self.capacity = capacity
        self._buffer: list[SyncEvent | None] = [None] * capacity
        self._head = 0   # index event tertua
        self._tail = 0   # index slot kosong berikutnya
        self._count = 0

    def push(self, note_id: int, action: str) -> SyncEvent:
        event = SyncEvent(note_id, action)
        self._buffer[self._tail] = event
        self._tail = (self._tail + 1) % self.capacity
        if self._count < self.capacity:
            self._count += 1
        else:
            # buffer penuh → geser head (timpa event terlama)
            self._head = (self._head + 1) % self.capacity
        return event

    def get_recent(self, n: int | None = None) -> list[SyncEvent]:
        """Ambil N event terakhir (default: semua)."""
        result = []
        for i in range(self._count):
            idx = (self._head + i) % self.capacity
            result.append(self._buffer[idx])
        if n:
            result = result[-n:]
        return result

    def get_unsynced(self) -> list[SyncEvent]:
        return [e for e in self.get_recent() if e and not e.synced]

    def mark_synced(self, note_id: int):
        for e in self.get_recent():
            if e and e.note_id == note_id:
                e.synced = True

    def __repr__(self):
        events = self.get_recent()
        return f"CircularBuffer({self._count}/{self.capacity}):\n" + \
               "\n".join(f"  {e}" for e in events)


# ─────────────────────────────────────────────
# 5. NOTEAPP – menggabungkan semua struktur
# ─────────────────────────────────────────────

class NoteApp:
    def __init__(self, sync_buffer_size: int = 10):
        self._notes: dict[int, Note]  = {}
        self._next_id                 = 1

        # struktur data utama
        self.tag_index      = MultiTagIndex()
        self.chrono_list    = SortedDoublyLinkedList(
                                key_fn=lambda n: n.created_at, reverse=True)  # terbaru dulu
        self.alpha_list     = SortedDoublyLinkedList(
                                key_fn=lambda n: n.title.lower())
        self.sync_buffer    = CircularSyncBuffer(sync_buffer_size)

    # ── CRUD ──────────────────────────────────

    def create_note(self, title: str, content: str, tags: list[str] = []) -> Note:
        note = Note(self._next_id, title, content)
        self._next_id += 1
        self._notes[note.note_id] = note

        for tag in tags:
            self.tag_index.add_note_tag(note, tag)

        self.chrono_list.insert(note)
        self.alpha_list.insert(note)
        self.sync_buffer.push(note.note_id, "CREATE")
        return note

    def delete_note(self, note_id: int) -> bool:
        if note_id not in self._notes:
            return False
        note = self._notes.pop(note_id)
        for tag in note.tags[:]:
            self.tag_index.remove_note_tag(note, tag)
        self.chrono_list.remove(note_id)
        self.alpha_list.remove(note_id)
        self.sync_buffer.push(note_id, "DELETE")
        return True

    def update_note(self, note_id: int, title: str = None, content: str = None):
        if note_id not in self._notes:
            return False
        note = self._notes[note_id]
        if title:
            # update di sorted list: hapus lalu insert ulang
            self.alpha_list.remove(note_id)
            note.title = title
            self.alpha_list.insert(note)
        if content:
            note.content = content
        self.sync_buffer.push(note_id, "UPDATE")
        return True

    def add_tag(self, note_id: int, tag: str):
        if note_id in self._notes:
            self.tag_index.add_note_tag(self._notes[note_id], tag)
            self.sync_buffer.push(note_id, "UPDATE")

    # ── VIEWS ─────────────────────────────────

    def view_chronological(self) -> list[Note]:
        return self.chrono_list.to_list()

    def view_alphabetical(self) -> list[Note]:
        return self.alpha_list.to_list()

    def view_by_tag(self, tag: str) -> list[Note]:
        return self.tag_index.get_notes_by_tag(tag)


# ─────────────────────────────────────────────
# DEMO
# ─────────────────────────────────────────────

if __name__ == "__main__":
    app = NoteApp(sync_buffer_size=5)

    print("=" * 55)
    print("  DEMO APLIKASI NOTE-TAKING")
    print("=" * 55)

    # Buat note
    n1 = app.create_note("Belajar Python",   "List, dict, OOP...",     ["python", "belajar"])
    n2 = app.create_note("Algoritma Sorting", "Bubble, merge, quick...", ["algoritma", "belajar"])
    n3 = app.create_note("Linked List",       "Singly, doubly, circular", ["algoritma", "python"])
    n4 = app.create_note("Catatan Harian",    "Hari ini belajar...",     ["harian"])

    # ── Tag Index ──────────────────────────
    print("\n[1] MULTI-LINKED BY TAG")
    print(f"  Tag 'python'    : {[n.title for n in app.view_by_tag('python')]}")
    print(f"  Tag 'algoritma' : {[n.title for n in app.view_by_tag('algoritma')]}")
    print(f"  Tag 'belajar'   : {[n.title for n in app.view_by_tag('belajar')]}")

    # ── Sorted Views ───────────────────────
    print("\n[2] CHRONOLOGICAL VIEW (terbaru dulu)")
    for n in app.view_chronological():
        print(f"  - {n.title}")

    print("\n[3] ALPHABETICAL VIEW")
    for n in app.view_alphabetical():
        print(f"  - {n.title}")

    # ── Sync Buffer ────────────────────────
    print("\n[4] SYNC BUFFER (5 event terakhir)")
    print(app.sync_buffer)

    # Simulasi update & sync
    app.update_note(n1.note_id, title="Belajar Python Lanjut")
    app.delete_note(n4.note_id)
    app.sync_buffer.mark_synced(n1.note_id)

    print("\n[5] SYNC BUFFER setelah update & delete")
    print(app.sync_buffer)

    print("\n[6] Unsynced events:")
    for e in app.sync_buffer.get_unsynced():
        print(f"  {e}")

    print("\n[7] ALPHABETICAL setelah update judul")
    for n in app.view_alphabetical():
        print(f"  - {n.title}")
