(function () {
    function r(e, n, t) {
        function o(i, f) {
            if (!n[i]) {
                if (!e[i]) {
                    var c = "function" == typeof require && require;
                    if (!f && c) return c(i, !0);
                    if (u) return u(i, !0);
                    var a = new Error("Cannot find module '" + i + "'");
                    throw a.code = "MODULE_NOT_FOUND", a
                }
                var p = n[i] = { exports: {} };
                e[i][0].call(p.exports, function (r) {
                    var n = e[i][1][r];
                    return o(n || r)
                }, p, p.exports, r, e, n, t)
            }
            return n[i].exports
        }

        for (var u = "function" == typeof require && require, i = 0; i < t.length; i++) o(t[i]);
        return o
    }

    return r
})()({
    1: [function (require, module, exports) {
        $(document).ready(function () {

            let elementPicker = require('element-picker');

            let feedback = `<div class="feedback__top"><span class="feedback__top_close"></span><h3 class="feedback__top_heading">Ay&uacute;danos</h3><p class="feedback__top_text">a mejorar el sitio</p><img src="userFeedback/static/img/developer_image.png" class="feedback__top_photo" alt="Developer logo"/></div><div class="feedback__bubble"><img src="userFeedback/static/img/developer_image.png" class="feedback__bubble_img" alt="Developer logo"/></div><div class="feedback__circle--1"></div><div class="feedback__circle--2"></div><div class="feedback"><p class="feedback__cancel">Cancelar <span class="fa-times"></span></p><div class="feedback__bottom"><form class="feedback__form" action="#"><button class="feedback__bottom_close icon" type="button"><span class="fa-times"></span></button><p class="feedback__bottom_text">¿C&oacute;mo calificar&iacute;as tu experiencia?</p><div class="feedback__bottom_rating"><input type="radio" id="star5" name="rating" value="5" /><label class="full" for="star5" title="Excelente - 5 estrellas"><div class="u-triangle"></div></label><input type="radio" id="star4" name="rating" value="4" /><label class="full" for="star4" title="Muy buena - 4 estrellas"><div class="u-triangle"></div></label><input type="radio" id="star3" name="rating" value="3" /><label class="full" for="star3" title="Meh - 3 estrellas"><div class="u-triangle"></div></label><input type="radio" id="star2" name="rating" value="2" /><label class="full" for="star2" title="Media mala - 2 estrellas"><div class="u-triangle"></div></label><input type="radio" id="star1" name="rating" value="1" /><label class="full" for="star1" title="Muy mala - 1 estrella"><div class="u-triangle"></div></label></div><div class="feedback__bottom_description"><textarea name="description" placeholder="Cu&eacute;ntanos sobre tu experiencia..." class="feedback__bottom_description--area" id="feedback_text"></textarea><div class="feedback__bottom_description--highlight"><span class="fa-border-style"></span><span class="fas-text">Ha seleccionado un elemento</span><span class="tooltiptext">Seleccione un elemento de la pantalla</span></div><button type="button" class="feedback__bottom_description--send">Enviar</button></div></form></div></div><div class="feedback__message"><div class="feedback__message_text"><h2 class="feedback__message_heading">¡Gracias!</h2><p class="feedback__message_p">Sus comentarios nos son muy valiosos</p><p class="feedback__message_p">Le aseguramos que ser&aacute;n tomados en cuenta</p></div><img src="userFeedback/static/img/developer_image.png" class="feedback__message_photo" alt="Developer logo"></div>`;

            $('body').append(feedback);

            let bottom_close = $('.feedback__bottom_close');
            let bottom = $('.feedback__bottom');
            let message = $('.feedback__message');
            let bubble0 = $('.feedback__bubble');
            let bubble1 = $('.feedback__circle--1');
            let bubble2 = $('.feedback__circle--2');
            let top_close = $('.feedback__top_close');
            let top = $('.feedback__top');
            let cancel = $('.feedback__cancel');
            let bottom_desc = $('.feedback__bottom_description');
            let bottom_text = $('.feedback__bottom_description--area');
            let ratings = $('.feedback__bottom_rating > label');
            let highlighter = $('.fa-border-style');
            let body = $('body *');
            let allowed_targets = body.not('.feedback *, .feedback');
            let grey_text = $('.fas-text');
            let send = $('.feedback__bottom_description--send');
            let selected_element, dataURL, x_coord, y_coord;

            function deselect(elem) {
                $(elem).removeClass('u-outline');
                $(elem).removeClass('u-box-shadow');
                $(elem).removeClass('u-highlighted');
            }

            function deselect_all(elems, except = null) {
                elems.each(function (_, elem) {
                    deselect($(elem));
                });
                if (except) {
                    select(except);
                }
            }

            function message_appear() {
                feedback_message.css({ 'visibility': 'visible' });
                feedback_message.animate({ 'opacity': 1 });
            }

            function init_state_top() {
                deselect_all(allowed_targets);
            }

            function init_state_bottom() {
                bottom.css('display', 'none');
                bottom.css('opacity', '0');
                bottom_desc.css({ 'height': 0 });
                bottom_text.css({ 'height': 0 });
                bottom_desc.css({ 'overflow': 'hidden' });
                grey_text.css('color', '#4d5051');
                $('.feedback__bottom_rating > input').each((_, elem) => $(elem).prop('checked', false));
            }

            function top_appear(initTime) {
                init_state_top();
                setTimeout(function () {
                    bubble1.fadeIn(300);
                }, initTime);
                setTimeout(function () {
                    bubble2.fadeIn(300);
                }, initTime + 300);
                setTimeout(function () {
                    top.fadeTo(300, 1);
                }, initTime + 600);
            }

            function top_disappear(time) {
                top.fadeOut(time);
                setTimeout(() => bubble2.fadeOut(time), time);
                setTimeout(() => bubble1.fadeOut(time), time * 2);
            }

            function bottom_appear(init = true) {
                if (init) {
                    init_state_bottom();
                }
                bottom.css("display", 'block');
                bottom.animate({ "opacity": 1 }, 300);
            }

            function bottom_disappear(init = true) {
                bottom.css("display", 'none');
                ratings.find('.u-triangle').css({ 'opacity': 0 });
                bottom.animate({ "opacity": 0 }, 300);
                if (init) {
                    init_state_bottom();
                }
            }

            function cancel_appear() {
                bottom_disappear(init = false);
                cancel.css("display", 'block');
                cancel.animate({ "opacity": 1 }, 300);
            }

            function cancel_disappear() {
                cancel.css("display", 'none');
                cancel.animate({ "opacity": 0 }, 300);
            }

            function screen_shot(element) {
                const a = document.body;
                element.classList.add('u-border');
                html2canvas(a).then(canvas => {
                    dataURL = canvas.toDataURL();
                    send.click(function () {
                        sendInformation();
                        bottom_disappear();
                        message_appear();
                        window.setTimeout(() => location.reload(), 1000);
                    });
                    element.classList.remove('u-border');
                });
            }

            top.fadeOut(0);
            bubble0.fadeOut(0);
            bubble1.fadeOut(0);
            bubble2.fadeOut(0);
            top_appear(1000);
            init_state_bottom();

            top.click(function (e) {
                if (!$(e.target).is(top_close)) {
                    top_disappear(200);
                    setTimeout(function () {
                        bottom_appear()
                    }, 800);
                }
            });

            bubble0.click(function () {
                bubble0.fadeOut(200);
                top_appear(200);
            })

            top_close.click(function () {
                top_disappear(300);
                setTimeout(() => bubble0.fadeIn(300), 300 * 2.5);
            });

            bottom_close.click(function (event) {
                event.preventDefault();
                deselect_all(allowed_targets);
                bottom_disappear();
                top_appear(200);
            });

            ratings.click(function (e) {
                ratings.find('.u-triangle').css({ 'opacity': 0 });
                $(e.target).find('.u-triangle').css({ 'opacity': 1 });
                bottom_desc.css({ 'overflow': 'visible' });
                bottom_desc.animate({ 'height': '180px' }, 150);
                bottom_text.animate({ 'height': '91px' }, 150);
            });

            highlighter.click(function (event) {
                event.stopPropagation();
                deselect_all(allowed_targets);
                cancel_appear();
                bottom_disappear(init = false);
                elementPicker.init({
                    onClick,
                    backgroundColor: 'rgba(0, 0, 0, 0.3)',
                    except: $('.feedback *, .feedback')
                });
            });

            function onClick(element, [x, y]) {
                selected_element = element.outerHTML;
                screen_shot(element);
                x_coord = x;
                y_coord = y;
                cancel_disappear();
                bottom_appear(init = false);
                grey_text.css('color', '#a0a0a0');

            }

            cancel.click(function () {
                cancel_disappear();
                elementPicker.reset();
                bottom_appear(init = false);
                deselect_all(allowed_targets);
                grey_text.css('color', '#4d5051');
            });

            function message_appear() {
                message.css({ 'visibility': 'visible' });
                message.animate({ 'opacity': 1 });
            }


            function objectifyForm(formArray) {//serialize data function

                var returnArray = {};
                for (var i = 0; i < formArray.length; i++) {
                    returnArray[formArray[i]['name']] = formArray[i]['value'];
                }
                return returnArray;
            }

            function sendInformation() {
                let formArray = $('.feedback__form').serializeArray();
                form = objectifyForm(formArray);
                form['selected_element'] = selected_element;
                form['screen_shot'] = dataURL;
                form['page_URL'] = window.location.href;
                form['x_coord'] = x_coord;
                form['y_coord'] = y_coord;
                $.ajax({
                    url: '/user_feedback/save_feedback',
                    type: 'post',
                    cache: false,
                    data: form,
                    success: function (data) {
                        console.log(data);
                    },
                    error: function (err) {
                        console.log(err);
                    }
                });
                return false;
            }


        });
    }, { "element-picker": 2 }], 2: [function (require, module, exports) {
        /**!
         * Element Picker.
         * A JavaScript library that allows you to point and click to get the hovered element.
         * @author  James Bechet <jamesbechet@gmail.com>
         * @license MIT
         */

        (function elementPickerModule(factory) {

            if (typeof define === 'function' && define.amd) {
                define(factory);
            } else if (typeof module != 'undefined' && typeof module.exports != 'undefined') {
                module.exports = factory();
            } else {
                window['elementPicker'] = factory();
            }
        })(function elementPickerFactory() {

            if (typeof window === 'undefined' || !window.document) {
                console.error('elementPicker requires the window and document.');
            }

            var oldTarget;
            var desiredBackgroundColor = 'rgba(0, 0, 0, 0.1)';
            var oldBackgroundColor;
            var onClick;

            function onMouseMove(event) {

                event = event || window.event;
                var target = event.target || event.srcElement;
                if (oldTarget) {
                    resetOldTargetColor();
                } else {
                    document.body.style.cursor = 'pointer';
                }
                if (!$(event.target).is(except)) {
                    oldTarget = target;
                    oldBackgroundColor = target.style.backgroundColor;
                    target.style.backgroundColor = desiredBackgroundColor;
                }

            }

            function onMouseClick(event) {

                event = event || window.event;
                var target = event.target || event.srcElement;
                if (event.preventDefault) event.preventDefault();
                if (event.stopPropagation) event.stopPropagation();
                console.log(event.altKey);
                if (!$(target).is(except)) {
                    onClick(target, [event.clientX, event.clientY]);
                }
                reset();
                return false;

            }

            function reset() {

                document.removeEventListener('click', onMouseClick, false);
                document.removeEventListener('mousemove', onMouseMove, false);
                document.body.style.cursor = 'auto';
                if (oldTarget) {
                    resetOldTargetColor();
                }
                oldTarget = null;
                oldBackgroundColor = null;

            }

            function resetOldTargetColor() {
                oldTarget.style.backgroundColor = oldBackgroundColor
            }

            function recursiveUnbind($jElement) {
                // remove this element's and all of its children's click events
                $jElement.unbind();
                $jElement.removeAttr('onclick');
                $jElement.children().each(function () {
                    if (!$jElement.is(except)) {
                        recursiveUnbind($(this));
                    }
                });
            }

            function init(options) {

                if (!options || !options.onClick) {
                    console.error('onClick option needs to be specified.');
                    return;
                }

                desiredBackgroundColor = options.backgroundColor || desiredBackgroundColor
                onClick = options.onClick;
                except = options.except;

                recursiveUnbind($(document));
                document.addEventListener('click', onMouseClick, false);
                document.addEventListener('mousemove', onMouseMove, false);

                return elementPicker;

            }

            /**
             * The library object.
             * @property {Function} init    - Function called to init the library.
             * @property {Function} onClick - The callback triggered once an element is clicked.
             * @property {String} version   - The library's version.
             * @type {Object}
             */
            var elementPicker = {};
            elementPicker.version = '1.0.1';
            elementPicker.init = init;
            elementPicker.reset = reset;

            return elementPicker;

        });

    }, {}]
}, {}, [1]);