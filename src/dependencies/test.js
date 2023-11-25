function delete_group(group_name, counter_identifier, button_id, additional_counter_identifiers=[]) {
                        var index = parseInt(button_id.split(".")[2])
                        var final_element_selector = window[counter_identifier] - 1
                        var container_selector = "#" + group_name + "\\." + index

                        console.log("*** START ***")
                        console.log(counter_identifier)
                        console.log(final_element_selector)
                        console.log(container_selector)
                        console.log(index)
                        console.log("*** END ***")

                        //delete the selected container
                        $(container_selector)[0].remove()


                        // get all the items in the group past the deleted element and rename them
                        for (var i = index + 1; i <= final_element_selector; i++) {
                            console.log("*** STARTING RENAME ***")
                          var new_index = i - 1
                            var elements_selector = ":regex(name,^" + group_name + ".(.*)." + i + ")"
                            console.log(elements_selector)
                            $(elements_selector).each(function() {
                              var old_name = this.name
                              if (old_name.includes(".")){
                              if (old_name.match(/\./g).length == 4 || old_name.match(/\./g).length == 3){

                                this.name= old_name.replace(/[0-9]/, new_index)

                              }else{
                                this.name= old_name.replace(/\.([^.]*)$/, "." + new_index)
                              }
                            }
                            })
                            var elements_selector = ":regex(id,^" + group_name + ".(.*)." + i + ")"
                            $(elements_selector).each(function() {
                              var old_id = this.id
                              if (old_id.includes(".")){
                                  console.log(old_id);
                              if (old_id.match(/\./g).length == 4 || old_id.match(/\./g).length == 3){
                                this.id= old_id.replace(/[0-9]/, new_index)


                              }else{
                                this.id= old_id.replace(/\.([^.]*)$/, "." + new_index)
 

                              }}
                            })


                            
                            var elements_selector = ":regex(id,^df" + group_name + ".(.*)." + i + ")"
                            $(elements_selector).each(function() {
                                console.log("*** STARTING REID ***")
                              var old_id = this.id
                              if (old_id.includes(".")){

                              if (old_id.match(/\./g).length == 4 || old_id.match(/\./g).length == 3){
                                this.id= old_id.replace(/[0-9]/, new_index)


                              }else{
                                this.id= old_id.replace(/\.([^.]*)$/, "." + new_index)
 

                              }}
                              console.log("*** ENDING REID ***")
                            })

                            // rename container to match new index
                            var container_selector = "#" + group_name + "\\." + i
                            $(container_selector)[0].id = $(container_selector)[0].id.replace(/\.([^.]*)$/, "." + new_index)

                            



                    }

                    // hack for ipipeline benefits bug do not use elsewhere and fix the bug (2 names are being set) when you can
                    if (group_name == "BenefitList") {
                        group_name = "Benefits"

                         // get all the items in the group past the deleted element and rename them
                         for (var i = index + 1; i <= final_element_selector; i++) {
                            console.log("*** STARTING RENAME ***")
                          var new_index = i - 1
                            var elements_selector = ":regex(name,^" + group_name + ".(.*)." + i + ")"
                            console.log(elements_selector)
                            $(elements_selector).each(function() {
                              var old_name = this.name
                              if (old_name.includes(".")){
                              if (old_name.match(/\./g).length == 4 || old_name.match(/\./g).length == 3){

                                this.name= old_name.replace(/[0-9]/, new_index)

                              }else{
                                this.name= old_name.replace(/\.([^.]*)$/, "." + new_index)
                              }
                            }
                            })
                            var elements_selector = ":regex(id,^" + group_name + ".(.*)." + i + ")"
                            $(elements_selector).each(function() {
                              var old_id = this.id
                              if (old_id.includes(".")){
                                  console.log(old_id);
                              if (old_id.match(/\./g).length == 4 || old_id.match(/\./g).length == 3){
                                this.id= old_id.replace(/[0-9]/, new_index)


                              }else{
                                this.id= old_id.replace(/\.([^.]*)$/, "." + new_index)
 

                              }}
                            })


                            
                            var elements_selector = ":regex(id,^df" + group_name + ".(.*)." + i + ")"
                            $(elements_selector).each(function() {
                                console.log("*** STARTING REID ***")
                              var old_id = this.id
                              if (old_id.includes(".")){

                              if (old_id.match(/\./g).length == 4 || old_id.match(/\./g).length == 3){
                                this.id= old_id.replace(/[0-9]/, new_index)


                              }else{
                                this.id= old_id.replace(/\.([^.]*)$/, "." + new_index)
 

                              }}
                              console.log("*** ENDING REID ***")
                            })

                            



                    }




                    }

                    window[counter_identifier] = window[counter_identifier] - 1
                  }
