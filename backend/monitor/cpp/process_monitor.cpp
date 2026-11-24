
#include <cctype>
#include <fstream>
#include <iostream>
#include <sstream>
#include <string>

using namespace std;

// Escape special characters for valid JSON strings
string escape_json(string value) {
  string result;

  for (char ch : value) {
    if (ch == '"' || ch == '\\') {
      result += '\\';
    }

    if (ch == '\n') {
      result += "\\n";
    } else if (ch == '\r') {
      result += "\\r";
    } else if (ch == '\t') {
      result += "\\t";
    } else {
      result += ch;
    }
  }

  return result;
}

int main(int argc, char *argv[]) {

  if (argc != 2) {
    cerr << "Usage: process_monitor <PID>" << endl;
    return 1;
  }

  string pid = argv[1];

  for (char ch : pid) {
    if (!isdigit(static_cast<unsigned char>(ch))) {
      cerr << "Invalid PID." << endl;
      return 1;
    }
  }

  if (stoll(pid) <= 0) {
    cerr << "Invalid PID." << endl;
    return 1;
  }

  string path = "/proc/" + pid;

  ifstream stat_file(path + "/stat");

  if (!stat_file.is_open()) {
    cerr << "Process not found or access denied." << endl;
    return 1;
  }

  string line;
  getline(stat_file, line);

  size_t start = line.find('(');
  size_t end = line.rfind(')');

  if (start == string::npos || end == string::npos) {
    cerr << "Could not read process information." << endl;
    return 1;
  }

  string name = line.substr(start + 1, end - start - 1);

  istringstream data(line.substr(end + 2));

  char state;
  int ppid;

  if (!(data >> state >> ppid)) {
    cerr << "Could not read parent process ID." << endl;
    return 1;
  }

  ifstream cmd_file(path + "/cmdline");
  string command;
  char ch;

  while (cmd_file.get(ch)) {
    if (ch == '\0') {
      command += ' ';
    } else {
      command += ch;
    }
  }

  // Output process information as JSON
  cout << "{";
  cout << "\"pid\":" << pid << ",";
  cout << "\"ppid\":" << ppid << ",";
  cout << "\"name\":\"" << escape_json(name) << "\",";
  cout << "\"state\":\"" << state << "\",";
  cout << "\"command\":\"" << escape_json(command) << "\"";
  cout << "}" << endl;

  return 0;
}
