#pragma once

#include <windows.h>
#include <string>

class INIReader {
public:
    explicit INIReader(const std::string& filename) : filename_(filename) {}

    int ParseError() const { return 0; }

    bool GetBoolean(const std::string& section, const std::string& name, bool defaultValue) const {
        char buffer[32] = {};
        GetPrivateProfileStringA(
            section.c_str(),
            name.c_str(),
            defaultValue ? "true" : "false",
            buffer,
            static_cast<DWORD>(sizeof(buffer)),
            filename_.c_str());

        std::string value(buffer);
        for (char& c : value) {
            if (c >= 'A' && c <= 'Z') c = static_cast<char>(c - 'A' + 'a');
        }
        return value == "1" || value == "true" || value == "yes" || value == "on";
    }

private:
    std::string filename_;
};
