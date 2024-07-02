# YpoxreotikiErgasia24_E20095_Mastoraki_Xristina-Eleni


# Πειρεχόμενα:
1. Παραδοχές
2. Τεχνολογίες που Χρησιμοποιήθηκαν
3. Περιγραφή των Αρχείων
4. Τρόπος Εκτέλεσης Συστήματος
5. Τρόπος Χρήσης του Συστήματος

# 1. Παραδοχές
Χρήστες και κατηγορίες: Οι χρήστες ανήκουν σε δύο κατηγορίες: γιατροί και ασθενείς.

Έλεγχος συνεδριών: Οι συνεδρίες χρηστών ελέγχονται για εγκυρότητα και πρόσβαση σε κατηγορίες.

Απαιτούμενα πεδία: Όλες οι εισαγωγές δεδομένων ελέγχονται για ύπαρξη απαιτούμενων πεδίων.

Αποφυγή διπλών εγγραφών: Χρησιμοποιούνται unique keys για να αποφεύγονται διπλές εγγραφές για γιατρούς και ασθενείς.


# 2. Τεχνολογίες που χρησιμοποιήθηκαν
Python, Flask, MongoDB, Docker & Docker Compose.

# 3. Περιγραφή των Αρχείων
-Dockerfile: Ορίζει το περιβάλλον Docker για την εφαρμογή Flask. Εγκαθιστά τις απαραίτητες βιβλιοθήκες και εξαρτήσεις.

-docker-compose.yml: Διαμορφώνει τις υπηρεσίες Docker για την εφαρμογή και τη βάση δεδομένων MongoDB. Προσδιορίζει τις θύρες και τις εξαρτήσεις μεταξύ των υπηρεσιών.

-main.py: Ο κύριος κώδικας της εφαρμογής Flask, περιέχει τα endpoints για τους χρήστες, τους γιατρούς, τους ασθενείς και τα ραντεβού.

# 4. Τρόπος Εκτέλεσης Συστήματος
Το container του MongoDB είναι υπεύθυνο για την αποθήκευση των δεδομένων, ενώ το container της εφαρμογής Flask χειρίζεται τα αιτήματα των χρηστών. Η εφαρμογή Flask επικοινωνεί με τη βάση δεδομένων MongoDB μέσω του PyMongo, μια βιβλιοθήκη που επιτρέπει τη σύνδεση και την εκτέλεση εντολών MongoDB από Python. Η διεύθυνση της βάσης δεδομένων MongoDB καθορίζεται στη μεταβλητή περιβάλλοντος MONGO_URI και είναι διαθέσιμη στην εφαρμογή Flask μέσω του αρχείου docker-compose.yml. Η εφαρμογή Flask διαθέτει διάφορα endpoints για τη διαχείριση των δεδομένων. Όταν ένας χρήστης στέλνει ένα αίτημα σε ένα από αυτά τα endpoints, η εφαρμογή εκτελεί τις απαραίτητες ενέργειες για την επεξεργασία του αιτήματος.

Η εισαγωγή δεδομένων γίνεται μέσω των POST αιτημάτων. Οι χρήστες μπορούν να προσθέσουν νέους γιατρούς, ασθενείς και ραντεβού στέλνοντας τα κατάλληλα JSON δεδομένα στα αντίστοιχα endpoints. Κάθε φορά που εισάγονται νέα δεδομένα, η εφαρμογή ελέγχει αν υπάρχουν τα απαραίτητα πεδία, προσθέτει τα δεδομένα στη βάση και επιστρέφει το αποτέλεσμα της ενέργειας. Επίσης οι χρήστες μπορούν να ανακτούν δεδομένα για συγκεκριμένους γιατρούς, ασθενείς και ραντεβού χρησιμοποιώντας τα GET αιτήματα με τα αντίστοιχα αναγνωριστικά. Οι χρήστες μπορούν να ανακτούν δεδομένα για συγκεκριμένους γιατρούς, ασθενείς και ραντεβού χρησιμοποιώντας τα GET αιτήματα με τα αντίστοιχα αναγνωριστικά.
Τα δεδομένα επιστρέφονται σε μορφή JSON, επιτρέποντας την εύκολη χρήση τους από άλλες εφαρμογές ή interfaces.





# 5. Τρόπος Χρήσης του Συστήματος
Αρχικά εκτελούμε την εντολή "docker-compose up --build" για να δημιουργήσουμε τα Docker images και να ξεκινήοσυν τα containers. Ύστερα ανοίγουμε την διεύθυνση 'http://localhost:5000' όπου η εφαρμογή θα πρέπει να είναι διαθέσιμη. Εκεί θα μπορούμε να χρησιμοποιήσουμε τα παρα΄κάτω endpoints για την διαχείριση των δεδομένων των γιατρών, των ασθενών και των ραντεβού:

1. Εγγραφή γιατρών:

Endpoint: POST /api/v1/doctors
Σώμα αιτήματος (JSON):
(Παράδειγμα χρήσης)
{ "name": "Dr. John Doe",
   "specialization": "Cardiology",
   "username": "johndoe",
   "password": "password123"

}

2. Εγγραφή ασθενών:

Endpoint: POST /api/v1/patients
Σώμα αιτήματος (JSON):
json
Αντιγραφή κώδικα
{
  "name": "Jane Smith",
  "dob": "1985-08-15",
  "username": "janesmith",
  "password": "password123"
}

3.Δημιουργία ραντεβού:

Endpoint: POST /api/v1/appointments
Σώμα αιτήματος (JSON):
json
Αντιγραφή κώδικα
{
  "doctor_id": "60c72b2f5f1b2c001f8e4e61",
  "patient_id": "60c72b2f5f1b2c001f8e4e62",
  "date": "2023-07-10T10:00:00"
}

4.Προβολή πληροφοριών για γιατρούς:

Endpoint: GET /api/v1/doctors/<doctor_id>
Αντικαταστήστε <doctor_id> με το μοναδικό αναγνωριστικό του γιατρού.

5.Προβολή πληροφοριών ασθενών:

Endpoint: GET /api/v1/patients/<patient_id>
Αντικαταστήστε <patient_id> με το μοναδικό αναγνωριστικό του ασθενή.

6.Διαγραφή ραντεβού:

Endpoint: DELETE /api/v1/appointments/<appointment_id>
Αντικαταστήστε <appointment_id> με το μοναδικό αναγνωριστικό του ραντεβού που θέλετε να διαγράψετε.
